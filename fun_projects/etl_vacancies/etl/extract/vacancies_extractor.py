import json
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

def extract_vacancies_from_json(path: Path) -> list[dict]:
    logger.info("Reading vacancies from %s", path)

    with path.open() as file:
        data = json.load(file)

    if not isinstance(data, list):
        raise ValueError("Expected list of vacancies")

    logger.info("Extracted %s vacancies", len(data))
    return data
