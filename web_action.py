# web_action.py

from pathlib import Path
from time import sleep

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


WAIT_AMOUNT = 5
WAIT_AMOUNT_NO_STUDENT = 2

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
        assignment_link = WebDriverWait(driver, WAIT_AMOUNT_NO_STUDENT).until(
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

    sleep(0.2) # A small sleep is required!

    # Open answers.
    wait_click(driver, '//a[contains(@href,"/grading/review/")]')

    return True


def grade_one_cell(driver, index_in_base_cols: int, mapped_value: str):
    question_number = index_in_base_cols + 1
    criterium_number = mapped_value.strip("[]")  # Temporary fix: "[3]" -> "3"

    panel_xpath = f'(//div[@data-js-grading-panel=""])[{question_number}]'

    grade_xpath = (
        f'{panel_xpath}'
        f'//ul[contains(@class, "criteria--rubrics")]'
        f'//li[@data-js-criterium=""]'
        f'[.//*[@data-cy="select-criteria" and normalize-space()="{criterium_number}"]]'
        f'//*[@data-cy="select-criteria"]'
    )

    WebDriverWait(driver, WAIT_AMOUNT).until(
        EC.element_to_be_clickable((By.XPATH, grade_xpath))
    )

    grade_link = driver.find_element(By.XPATH, grade_xpath)
    grade_link.click()

    sleep(0.1)

    # Retrieve the surrounding <li> for the selected criterion.
    criterion_li = grade_link.find_element(By.XPATH, "./ancestor::li[1]")

    def add_comment(comment: str):
        comment_button = WebDriverWait(criterion_li, WAIT_AMOUNT).until(
            lambda li: li.find_element(By.CSS_SELECTOR, '[data-cy="comment-button"]')
        )

        try:
            comment_button.click()

        except Exception:
            # Existing comment already present.
            tooltip_button = WebDriverWait(criterion_li, WAIT_AMOUNT).until(
                lambda li: li.find_element(By.CSS_SELECTOR, 'button[data-controller="tooltip"]')
            )

            tooltip_button.click()

            edit_anchor = WebDriverWait(criterion_li, WAIT_AMOUNT).until(
                lambda li: li.find_element(By.XPATH, './/a[contains(@href, "/edit")]')
            )

            edit_anchor.click()

        comment_editor = WebDriverWait(criterion_li, WAIT_AMOUNT).until(
            lambda li: li.find_element(By.CSS_SELECTOR, '[contenteditable="true"]')
        )

        comment_editor.click()

        driver.execute_script(
            """
            const el = arguments[0];
            const text = arguments[1];

            el.focus();
            el.innerHTML = "";
            el.textContent = text;

            el.dispatchEvent(new Event('input', { bubbles: true }));
            el.dispatchEvent(new Event('change', { bubbles: true }));
            """,
            comment_editor,
            comment
        )

        sleep(0.5)

        submit_button = WebDriverWait(criterion_li, WAIT_AMOUNT).until(
            lambda li: li.find_element(By.CSS_SELECTOR, '[data-cy="submit-comment"]')
        )

        submit_button.click()

    return add_comment
