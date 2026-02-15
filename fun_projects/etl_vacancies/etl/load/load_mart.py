from sqlalchemy import text
from etl.db.connection import engine
import logging

logger = logging.getLogger(__name__)

REFRESH_MART_SQL = """
TRUNCATE TABLE vacancies_skill_stats;

INSERT INTO vacancies_skill_stats (skill, avg_salary, vacancies_count)
SELECT
    skill,
    AVG(
        CASE
            WHEN salary_from IS NOT NULL AND salary_to IS NOT NULL
                THEN (salary_from + salary_to) / 2
            WHEN salary_from IS NOT NULL
                THEN salary_from
            WHEN salary_to IS NOT NULL
                THEN salary_to
            ELSE NULL
        END
    )::INTEGER AS avg_salary,
    COUNT(*) AS vacancies_count
FROM staging_vacancies,
     UNNEST(skills) AS skill
GROUP BY skill;
"""

def refresh_skill_stats() -> None:
    with engine.begin() as conn:
        conn.execute(text(REFRESH_MART_SQL))

    logger.info("Mart vacancies_skill_stats refreshed")
