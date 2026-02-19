import json
from pathlib import Path
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)

def extract_vacancies_from_json(path: Path) -> List[Dict]:
    logger.info("Reading vacancies from %s", path)

    with path.open() as file:
        data = json.load(file)

    if not isinstance(data, list):
        raise ValueError("Expected list of vacancies")

    logger.info("Extracted %s vacancies", len(data))
    return data
