from pathlib import Path
import logging

from etl.extract.vacancies_extractor import extract_vacancies_from_json
from etl.load.load_raw import load_raw_vacancies

logging.basicConfig(level=logging.INFO)

if __name__ == "__main__":
    path = Path("data/raw/vacancies_2024_01_10.json")

    vacancies = extract_vacancies_from_json(path)
    load_raw_vacancies(vacancies)
