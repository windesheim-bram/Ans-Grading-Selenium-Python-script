# Automated Grading with Selenium

This project automates the process of grading student assignments using Selenium WebDriver. The script reads student data from an Excel spreadsheet and interacts with a web-based grading system to input grades.

## Prerequisites

- Python 3.12
- Selenium WebDriver
- ChromeDriver
- Google Chrome
- Pandas

## Installation

1. **Clone the repository:**

    ```sh
    git clone <repository-url>
    cd <repository-directory>
    ```

2. **Install the required Python packages:**

    ```sh
    pip install -r requirements.txt
    ```

3. **Download and install ChromeDriver:**

    Make sure ChromeDriver is installed and added to your system's PATH. You can download it from [here](https://sites.google.com/a/chromium.org/chromedriver/downloads).

4. **Set up Chrome for remote debugging:**

    Start Chrome with remote debugging enabled:

    ```sh
    /path/to/chrome --remote-debugging-port=9222 --user-data-dir=/Users/nielsarts/ChromeProfile
    ```

    Replace `/path/to/chrome` with the path to your Chrome executable.

## Configuration

1. **Update the assignment URL:**

    In the ``test_chrome.py`` file, update the ``url`` variable with the correct assignment URL:

    ```python
    url = "https://ans.app/assignments/1084506/results/"
    ```

2. **Update the file path:**

    In the ``test_chrome.py`` file, update the ``file_path`` variable with the path to your Excel file:

    ```python
    file_path = '/Users/nielsarts/Downloads/resultaten.xlsx'
    ```

## Usage

1. **Run the script:**

    ```sh
    python3 -m pytest run_grading.py -s
    ```

    The script will open Chrome, navigate to the assignment URL, and start grading based on the data in the Excel file.

## Notes

- Ensure that you are logged into the web application manually before running the script.
- The ChromeDriver should be running on port 9222.
- The script uses implicit and explicit waits to handle dynamic content loading.

## License

This project is licensed under the Apache License 2.0. See the LICENSE file for details.