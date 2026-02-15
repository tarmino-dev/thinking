from pathlib import Path
import logging

from etl.extract.vacancies_extractor import extract_vacancies_from_json
from etl.load.load_raw import load_raw_vacancies

from etl.extract.raw_reader import read_raw_vacancies
from etl.transform.vacancies_transformer import transform_vacancies
from etl.load.load_staging import load_staging_vacancies

logging.basicConfig(level=logging.INFO)

if __name__ == "__main__":
    # FILE -> RAW
    path = Path("data/raw/vacancies_2024_01_10.json")
    vacancies = extract_vacancies_from_json(path)
    load_raw_vacancies(vacancies)

    # RAW -> STAGING
    raw = read_raw_vacancies()
    transformed = transform_vacancies(raw)
    load_staging_vacancies(transformed)