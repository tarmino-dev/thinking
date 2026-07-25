import argparse
from datetime import date
from pathlib import Path
import logging

from etl.extract.vacancies_extractor import extract_vacancies_from_json, source_filename
from etl.load.load_raw import load_raw_vacancies

from etl.extract.raw_reader import read_raw_vacancies
from etl.transform.vacancies_transformer import transform_vacancies
from etl.load.load_staging import load_staging_vacancies

from etl.load.load_mart import refresh_skill_stats

logging.basicConfig(level=logging.INFO)

def main(run_date: date):
    # FILE -> RAW
    path = Path("data/raw") / source_filename(run_date)
    vacancies = extract_vacancies_from_json(path)
    load_raw_vacancies(vacancies)

    # RAW -> STAGING
    raw = read_raw_vacancies()
    valid, rejected = transform_vacancies(raw)
    if rejected:
        logging.warning("Skipped %s invalid vacancies: %s", len(rejected), rejected)
    if valid:
        load_staging_vacancies(valid)

    # STAGING -> SQL aggregation -> MART
    refresh_skill_stats()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the vacancies ETL pipeline")
    parser.add_argument(
        "--date",
        type=date.fromisoformat,
        default=date.today(),
        help="Source export date, YYYY-MM-DD (default: today)",
    )
    args = parser.parse_args()
    main(args.date)