# web_action.py

from pathlib import Path
from time import sleep

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


WAIT_AMOUNT = 5
WAIT_AMOUNT_NO_STUDENT = 3

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
                f'//a[contains(@href, "/results/") and contains(normalize-space(.), "{student_number}")]'
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

    # Find grading scheme dialog.
    try:
        dialog_button = WebDriverWait(driver, WAIT_AMOUNT).until(
            EC.element_to_be_clickable((
                By.CSS_SELECTOR,
                '[data-cy="view-grading-scheme"]'
            ))
        )

    except TimeoutException:
        print("❌ Could not open the grading scheme.")
        return False

    # Open grading scheme dialog.
    dialog_button.click()

    sleep(0.2)

    return True


def _safe_click(driver, element):
    try:
        element.click()
    except Exception:
        driver.execute_script("arguments[0].click();", element)


def _scroll_into_view(driver, element):
    driver.execute_script(
        "arguments[0].scrollIntoView({block: 'center'});",
        element
    )


def _hover(driver, *elements):
    actions = ActionChains(driver)

    for element in elements:
        actions.move_to_element(element).pause(0.1)

    actions.perform()


def _wait_for_visible_child(scope, selector: str):
    return WebDriverWait(scope, WAIT_AMOUNT).until(
        lambda parent: next(
            (
                el
                for el in parent.find_elements(By.CSS_SELECTOR, selector)
                if el.is_displayed()
            ),
            False
        )
    )


def _set_comment_text(driver, editor, comment: str):
    driver.execute_script(
        """
        const el = arguments[0];
        const text = arguments[1];

        el.focus();

        const escapeHtml = (value) => {
            const div = document.createElement("div");
            div.textContent = value;
            return div.innerHTML;
        };

        const normalized = text
            .replace(/\\r\\n/g, "\\n")
            .replace(/\\r/g, "\\n");

        el.innerHTML = normalized
            .split("\\n")
            .map(line => escapeHtml(line))
            .join("<br>");

        el.dispatchEvent(new InputEvent("input", {
            bubbles: true,
            inputType: "insertText",
            data: text
        }));

        el.dispatchEvent(new Event("change", {
            bubbles: true
        }));
        """,
        editor,
        str(comment)
    )


def _open_existing_comment_editor(driver, score_card, comment_frame):
    comment_frame_id = comment_frame.get_attribute("id")

    _hover(driver, score_card, comment_frame)

    dropdown_button = WebDriverWait(comment_frame, WAIT_AMOUNT).until(
        lambda frame: frame.find_element(
            By.CSS_SELECTOR,
            '[data-cy="dropdown-icon-button"]'
        )
    )

    _scroll_into_view(driver, dropdown_button)
    _safe_click(driver, dropdown_button)

    dropdown_menu = _wait_for_visible_child(
        comment_frame,
        '[data-cy~="dropdown-menu"]'
    )

    edit_link = dropdown_menu.find_element(
        By.CSS_SELECTOR,
        'a[href$="/edit"]'
    )

    _safe_click(driver, edit_link)

    editor_scope = WebDriverWait(driver, WAIT_AMOUNT).until(
        EC.presence_of_element_located((By.ID, comment_frame_id))
    )

    _wait_for_visible_child(
        editor_scope,
        '[contenteditable="true"]'
    )

    return editor_scope


def _open_new_comment_editor(driver, score_card):
    _hover(driver, score_card)

    comment_link = WebDriverWait(score_card, WAIT_AMOUNT).until(
        lambda card: card.find_element(
            By.CSS_SELECTOR,
            'a[href*="/criteria_comments/new"]'
        )
    )

    target_frame_id = comment_link.get_attribute("data-turbo-frame")

    if not target_frame_id:
        raise RuntimeError("Comment link has no data-turbo-frame target")

    _scroll_into_view(driver, comment_link)
    _safe_click(driver, comment_link)

    editor_scope = WebDriverWait(driver, WAIT_AMOUNT).until(
        EC.presence_of_element_located((By.ID, target_frame_id))
    )

    _wait_for_visible_child(
        editor_scope,
        '[contenteditable="true"]'
    )

    return editor_scope


def _add_or_update_comment(driver, score_card, comment: str):
    existing_comments = score_card.find_elements(
        By.CSS_SELECTOR,
        'turbo-frame[id^="criteria_comment_"]'
    )

    if existing_comments:
        editor_scope = _open_existing_comment_editor(
            driver,
            score_card,
            existing_comments[0]
        )
    else:
        editor_scope = _open_new_comment_editor(
            driver,
            score_card
        )

    comment_editor = _wait_for_visible_child(
        editor_scope,
        '[contenteditable="true"]'
    )

    _set_comment_text(
        driver,
        comment_editor,
        comment
    )

    sleep(0.3) # A small sleep is required!

    submit_button = WebDriverWait(editor_scope, WAIT_AMOUNT).until(
        lambda scope: scope.find_element(
            By.CSS_SELECTOR,
            'input[type="submit"][data-form-validation-target="submitButton"]'
        )
    )

    _safe_click(driver, submit_button)


def grade_one_cell(driver, index_in_base_cols: int, mapped_value: str):
    question_number = index_in_base_cols + 1
    criterium_number = int(mapped_value.strip("[]")) # Temporary fix: "[3]" -> "3"

    score_summary = WebDriverWait(driver, WAIT_AMOUNT).until(
        EC.presence_of_element_located((
            By.XPATH,
            f'(//turbo-frame[starts-with(@id, "score_submission_")])[{question_number}]'
        ))
    )

    question_container = driver.execute_script(
        """
        return arguments[0].closest('div.d-flex.flex-column.gap-4');
        """,
        score_summary
    )

    if question_container is None:
        raise RuntimeError(
            f"Could not find question container for question {question_number}"
        )

    score_cards = question_container.find_elements(
        By.CSS_SELECTOR,
        'div[data-cy="score"]'
    )

    if not 1 <= criterium_number <= len(score_cards):
        raise RuntimeError(
            f"Criterion {criterium_number} does not exist for question "
            f"{question_number}. Found {len(score_cards)} options."
        )

    score_card = score_cards[criterium_number - 1]

    classes = (score_card.get_attribute("class") or "").split()
    is_selected = "score--selected" in classes

    if not is_selected:
        _scroll_into_view(driver, score_card)
        _safe_click(driver, score_card)

    def add_comment(comment: str):
        _add_or_update_comment(
            driver,
            score_card,
            comment
        )

    return add_comment
