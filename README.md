# ATART: Academic Transcript Automatic Renaming Tool
### Video Demo:  [https://youtu.be/f9CFL15MWdA](https://youtu.be/f9CFL15MWdA)

> [!TIP]
> Watch this video to see how this tool works.

## Table of Contents

1. [About The Project](#about-the-project)
   - [Origin of the Idea](#origin-of-the-idea)
   - [Key Features](#key-features)
   - [Why Use This Tool?](#why-use-this-tool)
2. [How To Use](#how-to-use)
3. [Challenges and Limitations](#challenges-and-limitations)
4. [Credits](#credits)
5. [License](#license)


## About The Project

**ATART (Academic Transcript Automatic Renaming Tool)** is a Python-based utility designed for academic administration. It automates the manual process of opening scanned academic transcripts in PDF format, extracting student IDs via OCR (Optical Character Recognition) and search for names in a provided student list, and renaming the files accordingly.

### Origin of the Idea

The tool was originally developed to support the **Union of Students of the Faculty of Computer Science and Engineering** at my university. It is tailored to their specific workflow, but can be adapted for other academic or administrative batch-processing tasks with minor modifications.

### Key Features

- **Supports multiple sources:**
    + **Local mode:** _Works with files and spreadsheets stored on your machine._
    + **Online mode:** _Connects to Google Drive and Google Sheets via API._
- **OCR-based ID extraction:** _Reads only the cropped region containing the necessary data, ensuring speed without sacrificing accuracy._
- **Student name lookup:** _Cross-references extracted IDs with a provided student list (Excel/Google Sheets)._
- **Automatic renaming:** _Renames files to a standardized format (_`<StudentID>_Bảng điểm_<StudentName>.pdf`_)._

### Why Use This Tool?

As the number of transcripts grows, manually renaming each transcript becomes time-consuming and error-prone for union members. ATART significantly reduces this effort by processing all files in batch, making the task faster and easier.

## How To Use

ATART can be run in two modes: `local` (files on your computer) and `online` (files on Google Drive with a Google Sheet).

> [!IMPORTANT]
> Run requirements.txt to install required libraries.

```bash
pip install -r requirements.txt
```

### 1. Local Mode
Use this mode if all PDFs and the student list (Excel file) are stored on your computer.

**Steps:**
1. Place all transcript PDFs into a folder.
2. Set up `.env` file
    ```bash
    # local version
    FOLDER=<PATH_TO_FOLDER_WITH_PDFS>
    EXCEL=<PATH_TO_EXCEL_FILE>

    # headers
    COL_ID=<COLUMN_HEADER_FOR_STUDENT_ID>
    COL_NAME=<COLUMN_HEADER_FOR_STUDENT_NAME>
    SHEET_NAME=<SHEET_NAME_TO_BE_READ>
    ```
3. Prepare a student list in Excel (`.xlsx`) with at least columns that match `COL_ID` and `COL_NAME` you defined in `.env`.

4. Run the tool with:
   ```bash
   python project.py -m local
   ```
   Or simply run:
   ```bash
   python project.py
   ```
   as `local` mode is the default.
5. Renamed files will appear in the same folder in the format:
    ```bash
    <StudentID>_Bảng điểm_<StudentName>.pdf
    ```

### 2. Online Mode
Use this mode if PDFs are stored in Google Drive and the student list is in Google Sheets.

**Steps:**
1. Set up Google Drive API credentials (`client_secrets.json`) and place them in your project folder.
2. Prepare a student list in Google Sheets (`.xlsx`) with at least columns that match `COL_ID` and `COL_NAME` you defined in `.env`.
3. Write an Apps Script file that returns jsonified data of `COL_ID` and `COL_NAME`.
4. Share the Drive folder and Google Sheets with your API service account.
5. Set up `.env` file
    ```bash
    # online version
    FOLDER_ID=<ID_OF_FOLDER_WITH_PDFS>
    SHEETS_API_URL=<APPS_SCRIPT_DEPLOYMENT_URL>

    # headers
    COL_ID=<COLUMN_HEADER_FOR_STUDENT_ID>
    COL_NAME=<COLUMN_HEADER_FOR_STUDENT_NAME>
    SHEET_NAME=<SHEET_NAME_TO_BE_READ>
    ```
6. Run the tool with:
    ```bash
    python project.py -m online
    ```
7. Renamed files will be synced back to Google Drive in the format:
    ```bash
    <StudentID>_Bảng điểm_<StudentName>.pdf
    ```

### 3. Running Tests

This project uses [pytest](https://docs.pytest.org/) for testing.

#### Run full test with:

```bash
pytest test_project.py
```

#### Test each function:
```bash
pytest tests/test_project.py::test_function_name
```

> [!CAUTION]
> If you change anything related to the initial code, please change them in the file too.

## Challenges and Limitations

ATART is built with a very specific use case in mind: extracting student IDs from scanned academic transcripts and renaming the corresponding PDF files. While it performs this task effectively, there are still several challenges and limitations.

- Cropping areas are fixed; therefore, any transcript layout change in PDFs requires reconfiguration and fine-tuning of the cropping coordinates.
- OCR results can be affected by scan quality and can be tricked by some specific IDs. (i.e. OCR may failed to extract `1000001`)
- Online mode requires stable internet access and authorization with the Google Drive API. Any changes in Google’s API policies, quotas, or service outages can impact the tool’s availability.
- Online mode currently works with jsonified data from provided Apps Scipt API, not the Google Sheets or Excel file itself.
- ATART provide only 2 modes (`local` and `online`). This means _`local directories`_ with _`local excel file`_ and _`online folders`_ with _`Google Sheets`_, so you are unable to mix them.

## Credits

**Author:** Nguyễn Tiến Đạt

**University:** University of Technology - Vietnam National University of Ho Chi Minh City

**Libraries and Tools:**

- `pytesseract` for OCR

- `PyDrive2` for Google Drive integration

- `pandas` for data handling

- `tqdm` for progress bars

- `python-dotenv` for environment variable management

Special thanks to **Prof. David Malan** and **Mr. Carter Zenke** for the CS50P lectures and shorts, which inspired and guided the development of this project.

Gratitude also goes to the **open-source community** for creating and maintaining the tools that made this project possible.

## Lisence
This is free and unencumbered software released into the public domain.

Anyone is free to copy, modify, publish, use, compile, sell, or
distribute this software, either in source code form or as a compiled
binary, for any purpose, commercial or non-commercial, and by any
means.

In jurisdictions that recognize copyright laws, the author or authors
of this software dedicate any and all copyright interest in the
software to the public domain. We make this dedication for the benefit
of the public at large and to the detriment of our heirs and
successors. We intend this dedication to be an overt act of
relinquishment in perpetuity of all present and future rights to this
software under copyright law.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS BE LIABLE FOR ANY CLAIM, DAMAGES OR
OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
OTHER DEALINGS IN THE SOFTWARE.
