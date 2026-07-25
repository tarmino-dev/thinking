import json
from datetime import date
from pathlib import Path
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)


def source_filename(run_date: date) -> str:
    return f"vacancies_{run_date:%Y_%m_%d}.json"


def extract_vacancies_from_json(path: Path) -> List[Dict]:
    logger.info("Reading vacancies from %s", path)

    if not path.exists():
        raise FileNotFoundError(f"No vacancies export found: {path}")

    with path.open() as file:
        data = json.load(file)

    if not isinstance(data, list):
        raise ValueError("Expected list of vacancies")

    logger.info("Extracted %s vacancies", len(data))
    return data
