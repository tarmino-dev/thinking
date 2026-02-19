from sqlalchemy import text
from etl.db.connection import engine
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)

UPSERT_STAGING_SQL = """
INSERT INTO staging_vacancies (
    id,
    title,
    company,
    location,
    salary_from,
    salary_to,
    currency,
    experience,
    employment_type,
    published_at,
    skills
)
VALUES (
    :id,
    :title,
    :company,
    :location,
    :salary_from,
    :salary_to,
    :currency,
    :experience,
    :employment_type,
    :published_at,
    :skills
)
ON CONFLICT (id) DO UPDATE SET
    title = EXCLUDED.title,
    company = EXCLUDED.company,
    location = EXCLUDED.location,
    salary_from = EXCLUDED.salary_from,
    salary_to = EXCLUDED.salary_to,
    currency = EXCLUDED.currency,
    experience = EXCLUDED.experience,
    employment_type = EXCLUDED.employment_type,
    published_at = EXCLUDED.published_at,
    skills = EXCLUDED.skills,
    processed_at = NOW();
"""

def load_staging_vacancies(vacancies: List[Dict]) -> None:
    with engine.begin() as conn:
        conn.execute(text(UPSERT_STAGING_SQL), vacancies) # bulk insert

    logger.info("Loaded %s records into staging_vacancies", len(vacancies))
