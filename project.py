import re
import os
import fitz
import logging
import requests
import argparse
import numpy as np
import pandas as pd
from sys import exit
from PIL import Image
from tqdm import tqdm
from io import BytesIO
from pathlib import Path
from easyocr import Reader
from dotenv import load_dotenv
from warnings import filterwarnings
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive


# const
ID_PATTERN = re.compile(r"(?P<id>\d{7})")
BOLD = "\033[1m"
RESET = "\033[0m"
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW  = "\033[33m"
MAGENTA = "\033[35m"

# loggings and warnings
logging.getLogger("oauth2client").setLevel(logging.ERROR)
logging.basicConfig(level=logging.INFO, format="%(message)s")
filterwarnings("ignore", message="'pin_memory' argument is set as true")

# dotenv
load_dotenv()
excel = os.getenv("EXCEL")
folder = os.getenv("FOLDER")
api_url = os.getenv("SHEETS_API_URL")
folder_id = os.getenv("FOLDER_ID")
col_id = os.getenv("COL_ID")
col_name = os.getenv("COL_NAME")
sheet_name = os.getenv("SHEET_NAME")

# setup
p = Path(".")
reader = Reader(["en"], gpu=False, verbose=False)

# Authenticate with Google Drive
gauth = GoogleAuth()
gauth.ServiceAuth()
drive = GoogleDrive(gauth)

# parser
def parse_args():
    """
    Parse command-line arguments for execution mode

    :return: The chosen mode for execution, either "local" or "online"
    :rtype: str
    """
    parser = argparse.ArgumentParser(description="SV5T ATART: Rename PDF Academic Transcript with a specific format")
    parser.add_argument("-m", "--mode", choices=["local", "online"], default="local", help="Set mode: local/online", type=str)
    return parser.parse_args().mode


def main():
    """Prompt for a directory, extract student info from PDFs via OCR, and rename the files."""

    # parse mode
    global mode
    mode = parse_args()
    logging.info(f"Running on mode {BOLD}{MAGENTA}{mode}{RESET}")

    # Get files
    files = get_files(folder_id if mode == 'online' else folder, mode)
    if not files:
        exit(f"{YELLOW}No PDFs found in folder{RESET}")

    # Read data for id_to_name
    try:
        if mode == 'online':
            response = requests.get(api_url)
            data = response.json()
            if not data:
                exit(f"{YELLOW}Fetched nothing from API{RESET}")
            df = pd.DataFrame(data)
            id_to_name = dict(zip(df[col_id].astype(str), df[col_name]))
        else:
            df = pd.read_excel(excel, sheet_name=sheet_name)
            id_to_name = dict(zip(df[col_id].astype(str), df[col_name]))
    except (requests.RequestException, ValueError) as e:
        exit(f"{RED}Failed to load data: {e}{RESET}")
    except KeyError as e:
        exit(f"{RED}Missing `{e}`{RESET}")

    # processing
    total = len(files)
    succeeded = 0
    no_id, no_name = [], []

    with tqdm(total=total) as pbar:
        for file_info in files:
            if mode == 'online':
                student_id, student_name = process_file(file_info['id'], id_to_name, mode)
                filename = file_info["title"]
            else:
                student_id, student_name = process_file(file_info, id_to_name, mode)
                filename = file_info.name

            if student_id is None:
                no_id.append(filename)
                pbar.update(1)
                continue

            if student_name is None:
                no_name.append({"student_id": student_id, "filename": filename})
                pbar.update(1)
                continue

            succeeded += 1
            pbar.update(1)

    # summarize
    if succeeded:
        logging.info(f"{GREEN}{succeeded}/{total} succeeded{RESET}")
    if no_id or no_name:
        logging.error(f"{RED}{len(no_id) + len(no_name)}/{total} failed{RESET}")
    if no_id:
        for file in no_id:
            logging.error(f"{RED}Failed to get student id from {file}{RESET}")
    if no_name:
        for file in no_name:
            logging.error(f"{RED}Student with ID {file["student_id"]} from {file["filename"]} not exist{RESET}")


def get_files(folder, mode="local"):
    """
    Get the paths of all matched files in directory

    :param dir: Name of the directory
    :type dir: str
    :return: A list of PosixPaths of matched files
    :rtype: list
    """
    if mode == 'online':
        query = f"'{folder}' in parents and trashed=false and mimeType='application/pdf'"
        return drive.ListFile({"q": query, "fields": "items(id,title,mimeType)"}).GetList()
    else:
        return list(p.glob(f"./{folder}/*.pdf"))


def process_file(file_address, id_to_name, mode="local"):
    """
    OCR pdf file and rename if successful

    :param file_address: Path to PDF file
    :type file_address: PosixPath
    :param id_to_name: Dictionary of {<student_id>: <student_name>}
    :type id_to_name: dict
    :return: Student's id, student's name
    :rtype: str, str
    """

    student_id = get_id(file_address, mode)
    if not student_id:
        return None, None

    student_name = id_to_name.get(student_id)
    if not student_name:
        return student_id, None

    new_filename = format_name({"id": student_id, "name": student_name})
    if mode == 'online':
        rename_file(file_address, new_filename, mode)
    else:
        new_path = os.path.join(folder, new_filename)
        rename_file(file_address, new_path, mode)

    return student_id, student_name


def get_id(file_address, mode="local"):
    """
    Read data from pdf file

    :param file: File ID (online) or Path (local) to pdf file
    :type file: str or PosixPath
    :return: Student's id
    :rtype: str
    """
    if mode == 'online':
        file = drive.CreateFile({"id": file_address})
        buffer = file.GetContentIOBuffer()
        pdf_bytes = buffer.read()
        try:
            doc = fitz.open("pdf", pdf_bytes)
            page = doc[1]
        except Exception:
            return None
    else:
        try:
            doc = fitz.open(file_address)
            page = doc[1]
        except Exception:
            return None

    rect = page.rect
    crop_area = fitz.Rect(rect.width * 0.1, rect.height * 0.15, rect.width * 0.18, rect.height * 0.18)
    for v_dpi in [100, 125]:
        pix = page.get_pixmap(dpi=v_dpi, clip=crop_area)
        img = Image.open(BytesIO(pix.tobytes("png"))).convert("L")
        results = reader.readtext(np.array(img), detail=0)
        img.close()
        if student_id := get_data("\n".join(results)):
            doc.close()
            return student_id
    doc.close()
    return None


def get_data(text):
    """
    Extract student's name and id from text input

    :param text: Text data from pdf fie that OCR returned
    :type text: str
    :return: Student's id
    :rtype: str
    """
    if matches := ID_PATTERN.search(text):
        return matches["id"]
    return None


def format_name(data):
    """
    Format filename based on student's name and id

    :param data: A dictionary of student's name and id
    :type data: dict
    :return: A format str as filename
    :rtype: str
    """
    return f"{data['id']}_Bảng điểm_{data['name']}.pdf"


def rename_file(file_address, new_name, mode="local"):
    """
    Rename file with formatted name, add counter if duplicated

    :param file_address: File ID (online) or Path (local)
    :type file_address: str or PosixPath
    :param new_name: Formatted name (online) or full path (local) of file
    :type new_name: str
    """
    if mode == 'online':
        file = drive.CreateFile({"id": file_address})
        file["title"] = new_name
        file.Upload()
    else:
        base, ext = os.path.splitext(new_name)
        counter = 1
        current_name = new_name
        while os.path.exists(current_name):
            current_name = f"{base}_{counter}{ext}"
            counter += 1
        os.rename(file_address, current_name)


if __name__ == "__main__":
    main()
