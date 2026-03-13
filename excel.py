# excel.py

from pathlib import Path
from typing import Dict, List, Tuple, Optional

import pandas as pd

from config import AppConfig, ImportStrategy

from util import normalize_column_name


def load_sheet_dataframe_all(excel_path: Path, sheet_name: str) -> pd.DataFrame:
    return pd.read_excel(excel_path, sheet_name=sheet_name, engine="openpyxl")


def detect_columns_in_order(
    headers: List[str],
    cfg: AppConfig,
    strategy: ImportStrategy
) -> Tuple[List[str], List[str], Dict[str, Optional[str]]]:
    """
    Fuzzy matching:
    - match base columns using normalized strings
    - preserve original header order
    - if the column to the right CONTAINS comment_pattern (substring, fuzzy), include it
    """
    if not strategy.columns_to_import_norm_set:
        raise RuntimeError("columns_to_import must be defined for this import strategy")

    base_columns: List[str] = []
    comment_by_base: Dict[str, Optional[str]] = {}

    header_count = len(headers)

    headers_norm = [normalize_column_name(h) for h in headers]

    for i, (header, header_norm) in enumerate(zip(headers, headers_norm)):
        if header_norm not in strategy.columns_to_import_norm_set:
            continue

        base_columns.append(header)
        
        comment_header = None

        if i + 1 < header_count:
            right_header = headers[i + 1]
            right_norm = headers_norm[i + 1]

            if cfg.comment_pattern and cfg.comment_pattern in right_norm:
                comment_header = right_header

        comment_by_base[header] = comment_header

    return base_columns, comment_by_base
