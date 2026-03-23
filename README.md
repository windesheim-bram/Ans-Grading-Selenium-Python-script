# ANS Grading Selenium Python Script

A Python automation tool that imports assessment results from Excel into **ANS** using Selenium and Google Chrome remote debugging.

This tool supports:

* Multiple Excel sheets (groups)
* Multiple ANS assignments per Excel file
* Optional comment columns
* Configurable score mappings
* Skipping students

---

# 🚀 Prerequisites

* Python 3.9+
* Google Chrome (latest version recommended)
* ANS account with grading permissions
* Windows PowerShell (example commands below are Windows-based)

---

# 📦 Installation

## 1. Clone the repository

```powershell
git clone https://github.com/windesheim-bram/Ans-Grading-Selenium-Python-script.git
cd Ans-Grading-Selenium-Python-script
```

## 2. Install Python dependencies

```powershell
pip install -r requirements.txt
```

## 3. Install Google Chrome

Download and install Chrome from:

https://www.google.com/chrome/

---

# 🔧 Setup Chrome for Remote Debugging

Before running the script, you must start Chrome with remote debugging enabled.

### PowerShell example:

```powershell
& "C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir="C:\Users\user\ChromeProfile"
```

Notes:

* Adjust the path to Chrome if needed.
* `--user-data-dir` should point to a separate Chrome profile.
* After Chrome opens, **log in to ANS manually**.

---

# ⚙️ Configuration

The project requires:

* A `.env` file
* A `config.json` file

---

## 📄 .env file

Example:

```env
PATH_CONFIG=data\config.json
USER_DATA_DIR=C:\Users\user\ChromeProfile
```

| Variable        | Description                              |
| --------------- | ---------------------------------------- |
| `PATH_CONFIG`   | Path to your configuration file          |
| `USER_DATA_DIR` | Chrome profile used for remote debugging |

---

## 📄 config.json

This file controls how Excel columns map to ANS assignments.

| Key                                  | Required         | Description                            |
| ------------------------------------ | ---------------- | -------------------------------------- |
| `path_to_excel`                      | ✅                | Path to Excel file                     |
| `sheets_to_import`                   | ✅                | List of sheet (tab) names              |
| `import`                             | ✅                | List of import strategies              |
| `ans_assignment_id`                  | ✅ (per strategy) | ANS assignment ID                      |
| `columns_to_import`                  | ✅ (per strategy) | Excel columns used for that assignment |
| `column_student_id`                  | ✅                | Name of column containing student numbers      |
| `comment_pattern`                    | Optional         | Text identifying comment columns       |
| `comment_position`                   | Optional         | Position of comment columns       |
| `mapping`                            | ✅                | Ordered list of grading values         |
| `skip_till_including_student_number` | Optional         | Skip until this student number         |

---

## 📊 Example 1

### config.json

```json
{
    "path_to_excel": "data/results.xlsx",
    "sheets_to_import": [
        "results"
    ],
    "import": [
        {
            "ans_assignment_id": 1,
            "columns_to_import": [
                "1a",
                "1b",
                "1c"
            ]
        }
    ],
    "column_student_id": "Studentnummer",
    "comment_pattern": "Opmerking",
    "comment_position": "right",
    "mapping": ["0", "1", "2", "4"],
    "skip_till_including_student_number": null
}
```

### Example Excel Layout

| Studentnummer | 1a | 1a-opmerking | 1b | 1b-opmerking      | 1c | 1c-opmerking      |
| ------------- | -- | ------------ | -- | ----------------- | -- | ----------------- |
| 123456        | 4  | Good work    | 2  | Improve structure | 1  |                   |
| 234567        | 2  |              | 4  | Nice structure    | 2  |                   |

---

## 📊 Example 2

### config.json

```json
{
    "path_to_excel": "data/results.xlsx",
    "sheets_to_import": [
        "AB",
        "CD",
        "EF"
    ],
    "import": [
        {
            "ans_assignment_id": 1,
            "columns_to_import": [
                "DP1-1a",
                "DP1-1b"
            ]
        },
        {
            "ans_assignment_id": 2,
            "columns_to_import": [
                "DP2-1a",
                "DP2-1b"
            ]
        }
    ],
    "column_student_id": "Studentnummer",
    "comment_pattern": "Opmerking",
    "comment_position": "left",
    "mapping": ["0", "1", "2", "4"],
    "skip_till_including_student_number": null
}
```

### Example Excel Layout

| Studentnummer | DP1-Opmerking | DP1-1a | DP1-1b | DP2-Opmerking | DP2-1a | DP2-1b |
| ------------- | ------------- | ------ | ------ | ------------- | ------ | ------ |
| 123456        | Nice          | 4      | 1      | Good          | 2      | 1      |
| 234567        |               | 0      | 0      |               | 0      | 0      |

---

# 🏃 Usage

1. Start Google Chrome with remote debugging enabled
2. Ensure you are logged in to ANS in the opened Chrome window
3. Run the script:

```bash
python3 main.py
```

3. Keep the Chrome window focused while the script is running
4. Wait until all sheets and assignments have been processed

---

# 📝 Notes

* Chrome must be running with `--remote-debugging-port=9222`
* Make sure the Chrome window is focused during execution
* After importing a sheet, the program may need time before the next sheet can be processed
* Student numbers starting with `S` or `s` are automatically normalized
* Excel headers are matched fuzzily (case and whitespace insensitive)
* For each assignment column, the corresponding comment column must appear immediately to its right in the Excel sheet
* Comment columns are detected based on `comment_pattern`
* Large Excel files may take time to process

---

# ⚠️ Known Limitations

* Uses absolute XPaths (layout changes in ANS may break the script)
* Requires visible browser (not fully headless-safe)
* Selenium interactions depend on page stability
* `skip_till_including_student_number` applies globally (not per sheet) and only works on sheets containing the specified student number

---

# 📄 License

Licensed under the **Apache License 2.0**.

You may use, modify, and distribute this software under the terms of the Apache License 2.0.
