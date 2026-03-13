# main.py

from typing import Dict, Optional

import pandas as pd
from dotenv import load_dotenv
from selenium import webdriver

from config import AppConfig, ImportStrategy, require_env_path, load_config
from excel import detect_columns_in_order, load_sheet_dataframe_all  
from web_action import make_driver, open_student_submission, grade_one_cell, fill_comment

from util import normalize_column_name, normalize_value, normalize_value_student_number


def map_score(mapping: Dict[str, str], value) -> Optional[str]:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    
    key = str(value).strip()

    return mapping.get(key)


def should_write_comment(comment) -> bool:
    if comment is None:
        return False
    
    if not isinstance(comment, str):
        return False
    
    return bool(comment.strip())


def process_sheet_df(driver: webdriver.Chrome, cfg: AppConfig, strategy: ImportStrategy, sheet_name: str, df: pd.DataFrame):
    df_col_by_norm = {normalize_column_name(c): c for c in df.columns}

    headers = [str(c) for c in df.columns]

    base_columns, comment_by_base = detect_columns_in_order(headers, cfg, strategy)

    student_col = df_col_by_norm.get(normalize_column_name(cfg.column_student_id), cfg.column_student_id)

    start_processing = cfg.skip_till_including_student_number is None

    for _, row in df.iterrows():
        student_number = normalize_value_student_number(row.get(student_col, None))

        if not student_number:
            continue

        if not start_processing:
            if student_number == cfg.skip_till_including_student_number:
                start_processing = True
                continue

            print(f"Skipping student number: {student_number}")
            continue

        print(f"[assignment={strategy.assignment_id} sheet={sheet_name}] Grading student: {student_number}")

        is_success = open_student_submission(driver, strategy.assignment_id, student_number)

        if not is_success:
            continue

        for i, col in enumerate(base_columns):
            df_col = df_col_by_norm.get(normalize_column_name(col), col)
            raw_value = normalize_value(row.get(df_col))

            mapped_value = map_score(cfg.mapping, raw_value)

            if not mapped_value:
                print(f"  - {col}: empty/invalid ({raw_value})")
                continue

            grade_one_cell(driver, i, mapped_value)            
            print(f"  - {col}: {raw_value} -> {mapped_value}")

            comment_header = comment_by_base.get(col)

            if comment_header:
                df_comment_col = df_col_by_norm.get(normalize_column_name(comment_header), comment_header)
                comment = row.get(df_comment_col, "")
                
                if should_write_comment(comment):
                    fill_comment(driver, i, mapped_value, comment)
                    print(f"    comment: {comment}")


def main():
    load_dotenv()

    path_config = require_env_path("PATH_CONFIG")
    user_data_dir = require_env_path("USER_DATA_DIR")

    cfg = load_config(path_config)

    driver = make_driver(user_data_dir)

    try:
        # We load the df per sheet, to prevent reloading it when there are multiple strategies.
        for sheet in cfg.sheets_to_import:
            df = load_sheet_dataframe_all(cfg.spreadsheet_path, sheet)

            for strategy in cfg.import_strategies:
                process_sheet_df(driver, cfg, strategy, sheet, df)

    finally:
        driver.quit()


if __name__ == "__main__":
    main()
