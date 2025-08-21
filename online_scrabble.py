# online_scrabble.py
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
FOLDER_ID = os.getenv("FOLDER_ID")

# Authenticate with service account
gauth = GoogleAuth()
gauth.ServiceAuth()  # reads from settings.yaml
drive = GoogleDrive(gauth)

# Get all files in the folder
query = f"'{FOLDER_ID}' in parents and trashed=false and mimeType='application/pdf'"
file_list = drive.ListFile({'q': query}).GetList()

print(f"Found {len(file_list)} files.")

# Rename them sequentially
for i, file in enumerate(file_list, start=1):
    # Extract extension if exists
    _, ext = os.path.splitext(file['title'])
    if not ext:  # if no extension, leave blank
        ext = ""

    new_name = f"{i}{ext}"
    print(f"Renaming: {file['title']} -> {new_name}")

    file['title'] = new_name
    file.Upload()  # update name on Google Drive
