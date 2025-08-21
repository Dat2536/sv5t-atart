import os
from tqdm import tqdm
from project import get_files
from dotenv import load_dotenv

load_dotenv()
FOLDER = os.getenv("FOLDER")

def main():
    dir = FOLDER
    paths = get_files(dir)
    count = 0
    with tqdm(total=len(paths)) as pbar:
        for path in paths:
            count += 1
            root, ext = os.path.splitext(path)   # keep original extension
            new_name = f"{count}{ext}"
            os.rename(path, os.path.join(dir, new_name))
            pbar.update(1)

if __name__ == "__main__":
    main()
