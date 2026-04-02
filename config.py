# config.py

import os
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Set

from util import normalize_column_name, normalize_value_student_number


@dataclass(frozen=True)
class ImportStrategy:
    assignment_id: int
    columns_to_import_norm_set: Set[str]


@dataclass(frozen=True)
class AppConfig:
    spreadsheet_path: Path
    sheets_to_import: List[str]
    import_strategies: List[ImportStrategy]
    column_student_id: str
    comment_pattern: str
    comment_position: str
    mapping: Dict[str, str]
    skip_till_including_student_number: Optional[str]


def require_env_path(var_name: str) -> Path:
    value = os.environ.get(var_name)

    if not value:
        raise RuntimeError(f"Please specify {var_name} in .env")
    
    return Path(value).resolve()


def load_config(path_config: Path) -> AppConfig:
    cfg = json.loads(path_config.read_text(encoding="utf-8"))

    path_to_excel = cfg.get("path_to_excel")

    if not path_to_excel:
        raise RuntimeError("path_to_excel is empty in config")

    spreadsheet_path = Path(path_to_excel).resolve()

    sheets = cfg.get("sheets_to_import", []) or []

    if not sheets:
        raise RuntimeError("sheets_to_import is empty in config")

    import_list = cfg.get("import", []) or []

    if not import_list:
        raise RuntimeError("import is empty in config")

    import_strategies: List[ImportStrategy] = []

    for item in import_list:
        assignment_id = item.get("ans_assignment_id")

        if not assignment_id:
            raise RuntimeError("One of the import strategies has empty ans_assignment_id")

        cols = item.get("columns_to_import", []) or []

        if not cols:
            raise RuntimeError(f"columns_to_import is empty for assignment_id={assignment_id}")

        cols_norm_set = {normalize_column_name(c) for c in cols}

        import_strategies.append(
            ImportStrategy(
                assignment_id=int(assignment_id),
                columns_to_import_norm_set=cols_norm_set
            )
        )

    column_student_id = cfg.get("column_student_id", "Studentnummer")
    
    comment_pattern = cfg.get("comment_pattern", "opmerking")

    if comment_pattern:
        comment_pattern = normalize_column_name(comment_pattern)

    comment_position = str(cfg.get("comment_position", "right")).strip().lower()

    if comment_position not in {"right", "left"}:
        raise RuntimeError('comment_position must be "right" or "left"')

    mapping_list = cfg.get("mapping")
    
    if not mapping_list:
        raise RuntimeError("mapping is empty in config")

    mapping = {str(value).strip(): f"[{index + 1}]" for index, value in enumerate(mapping_list)}

    skip_value = cfg.get("skip_till_including_student_number", None)
    
    if skip_value:
        skip_value = normalize_value_student_number(skip_value)

    return AppConfig(
        spreadsheet_path=spreadsheet_path,
        sheets_to_import=list(sheets),
        import_strategies=import_strategies,
        column_student_id=column_student_id,
        comment_pattern=comment_pattern,
        comment_position=comment_position,
        mapping=mapping,
        skip_till_including_student_number=skip_value
    )
