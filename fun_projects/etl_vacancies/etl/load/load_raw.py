from sqlalchemy import text
from etl.db.connection import engine
import logging

logger = logging.getLogger(__name__)

UPSERT_RAW_SQL = """
INSERT INTO raw_vacancies (id, payload)
VALUES (:id, :payload)
ON CONFLICT (id) DO UPDATE
SET payload = EXCLUDED.payload,
    loaded_at = NOW();
"""

def load_raw_vacancies(vacancies: list[dict]) -> None:
    with engine.begin() as conn:
        for vacancy in vacancies:
            conn.execute(
                text(UPSERT_RAW_SQL),
                {
                    "id": vacancy["id"],
                    "payload": vacancy
                }
            )

    logger.info("Loaded %s records into raw_vacancies", len(vacancies))
