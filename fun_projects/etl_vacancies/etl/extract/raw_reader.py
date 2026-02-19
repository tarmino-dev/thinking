from sqlalchemy import text
from etl.db.connection import engine
from typing import List, Dict

SELECT_RAW_SQL = """
SELECT id, payload
FROM raw_vacancies;
"""

def read_raw_vacancies() -> List[Dict]:
    with engine.begin() as conn:
        result = conn.execute(text(SELECT_RAW_SQL))

        return [
            {
                "id": row.id,
                "payload": row.payload
            }
            for row in result
        ]
