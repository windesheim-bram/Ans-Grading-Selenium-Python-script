# web_action.py

from pathlib import Path
from time import sleep

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


WAIT_AMOUNT = 5

def make_driver(user_data_dir: Path) -> webdriver.Chrome:
    options = webdriver.ChromeOptions()
    options.add_argument(f"--user-data-dir={user_data_dir}")
    options.debugger_address = "localhost:9222"

    return webdriver.Chrome(options=options)


def wait_click(driver, xpath: str, timeout: int = WAIT_AMOUNT):
    WebDriverWait(driver, timeout).until(EC.element_to_be_clickable((By.XPATH, xpath)))
    driver.find_element(By.XPATH, xpath).click()


def wait_type(driver, by: By, selector: str, text: str, timeout: int = WAIT_AMOUNT):
    WebDriverWait(driver, timeout).until(EC.element_to_be_clickable((by, selector)))
    el = driver.find_element(by, selector)
    el.click()
    el.clear()

    # Hack to ensure updated UI and input focus.
    # Might not work. In that case, manualy enter a key in the input field, and run the script again.
    el.click()
    el.send_keys(text)


def open_student_submission(driver, assignment_id: int, student_number: str):
    url = f"https://ans.app/assignments/{assignment_id}/results"
    driver.get(url)

    # Search student with student id.
    wait_type(driver, By.ID, "search_items", student_number)

    # Wait for result list to contain student number.
    try:
        assignment_link = WebDriverWait(driver, WAIT_AMOUNT).until(
            EC.element_to_be_clickable((
                By.XPATH,
                f'//div[contains(@class,"text-support") and normalize-space()="{student_number}"]/ancestor::div[contains(@class,"d-flex")][1]//a'
            ))
        )

    except TimeoutException:
        print(f"❌ Student not found or timeout: {student_number}")
        return False

    # Open student page.
    assignment_link.click()

    # Open answers.
    wait_click(driver, "/html/body/div[4]/div/main/div/div[1]/div/div/a[2]/span")

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

    grade_xpath = (
        f"/html/body/main/div[1]/div[3]/div[3]/div/div[1]/div[{offset}]"
        f"/div{mapped_column}/ul[2]/li{mapped_value}/div[1]/a"
    )

    WebDriverWait(driver, WAIT_AMOUNT).until(
        EC.element_to_be_clickable((By.XPATH, grade_xpath))
    )

    grade_link = driver.find_element(By.XPATH, grade_xpath)
    grade_link.click()

    # Retrieve the surrounding <li> for the selected criterion.
    criterion_li = grade_link.find_element(By.XPATH, "./ancestor::li[1]")

    def add_comment(comment: str):
        comment_button = WebDriverWait(criterion_li, WAIT_AMOUNT).until(
            lambda li: li.find_element(By.CSS_SELECTOR, '[data-cy="comment-button"]')
        )

        comment_button.click()

        comment_editor = WebDriverWait(criterion_li, WAIT_AMOUNT).until(
            lambda li: li.find_element(By.CSS_SELECTOR, '[contenteditable="true"]')
        )

        comment_editor.click()
        comment_editor.send_keys(comment)

        sleep(0.5)

        submit_button = WebDriverWait(criterion_li, WAIT_AMOUNT).until(
            lambda li: li.find_element(By.CSS_SELECTOR, '[data-cy="submit-comment"]')
        )

        submit_button.click()

    return add_comment
