# web_action.py

from pathlib import Path
from time import sleep

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def make_driver(user_data_dir: Path) -> webdriver.Chrome:
    options = webdriver.ChromeOptions()
    options.add_argument(f"--user-data-dir={user_data_dir}")
    options.debugger_address = "localhost:9222"

    return webdriver.Chrome(options=options)


def wait_click(driver, xpath: str, timeout: int = 10):
    WebDriverWait(driver, timeout).until(EC.element_to_be_clickable((By.XPATH, xpath)))
    driver.find_element(By.XPATH, xpath).click()


def wait_type(driver, by: By, selector: str, text: str, timeout: int = 10):
    WebDriverWait(driver, timeout).until(EC.element_to_be_clickable((by, selector)))
    el = driver.find_element(by, selector)
    el.click()
    el.clear()
    el.send_keys(text)


def open_student_submission(driver, assignment_id: int, student_number: str):
    url = f"https://ans.app/assignments/{assignment_id}/results"
    driver.get(url)

    # Search student with student id.
    wait_type(driver, By.ID, "search_items", student_number, timeout=10)

    # Wait for result list to contain student number.
    try:
        WebDriverWait(driver, 10).until(
            EC.text_to_be_present_in_element(
                (By.XPATH, "/html/body/div[4]/div/main/div[4]/div/table/tbody/tr/td[2]/div/div[2]/div[2]"),
                str(student_number)
            )
        )
    except TimeoutException:
        print(f"❌ Student not found or timeout: {student_number}")
        return False

    # Open student page.
    wait_click(driver, "/html/body/div[4]/div/main/div[4]/div/table/tbody/tr/td[2]/div/div[2]/div[1]/a/span[1]", timeout=10)

    # Open answers.
    wait_click(driver, "/html/body/div[4]/div/main/div/div[1]/div/div/a[2]/span", timeout=10)

    return True


def _get_offset(driver, timeout: int = 2) -> int:
    """
    Returns the div index offset depending on whether
    the plagiarism warning banner is present.
    """

    plagiarism_xpath = "/html/body/main/div[1]/div[3]/div[3]/div/div[1]/div[1]/div/span"

    try:
        el = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.XPATH, plagiarism_xpath))
        )

        if "Plagiaat op vragen gedetecteerd" in el.text:
            return 2  # Shift by one extra div.

    except TimeoutException:
        pass

    return 1  # Normal situation.


def grade_one_cell(driver, index_in_base_cols: int, mapped_value: str):
    mapped_column = f"[{index_in_base_cols + 1}]"
    offset = _get_offset(driver)

    xpath = (
        f"/html/body/main/div[1]/div[3]/div[3]/div/div[1]/div[{offset}]"
        f"/div{mapped_column}/ul[2]/li{mapped_value}/div[1]/a"
    )

    wait_click(driver, xpath, timeout=15)


def fill_comment(driver, index_in_base_cols: int, mapped_value: str, comment: str):
    mapped_column = f"[{index_in_base_cols + 1}]"

    comment_button_xpath = (
        f"/html/body/main/div[1]/div[3]/div[3]/div/div[1]/div[2]/div{mapped_column}"
        f"/ul[2]/li{mapped_value}/div[2]/div[3]/div/a"
    )

    wait_click(driver, comment_button_xpath, timeout=10)

    comment_input_xpath = (
        f"/html/body/main/div[1]/div[3]/div[3]/div/div[1]/div[2]/div{mapped_column}"
        f"/ul[2]/li{mapped_value}/div[2]/div[3]/div[2]/form/div[1]/div/div[2]"
    )

    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, comment_input_xpath)))
    box = driver.find_element(By.XPATH, comment_input_xpath)
    box.click()
    box.send_keys(comment)
    
    sleep(0.5)

    save_button_xpath = (
        f"/html/body/main/div[1]/div[3]/div[3]/div/div[1]/div[2]/div{mapped_column}"
        f"/ul[2]/li{mapped_value}/div[2]/div[3]/div[2]/form/div[2]/button[2]"
    )

    wait_click(driver, save_button_xpath, timeout=10)
