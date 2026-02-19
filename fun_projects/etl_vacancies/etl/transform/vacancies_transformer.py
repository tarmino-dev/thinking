from datetime import datetime
from typing import List, Dict

def transform_vacancy(raw: dict) -> dict:
    payload = raw["payload"]

    return {
        "id": raw["id"],
        "title": payload.get("title"),
        "company": payload.get("company"),
        "location": payload.get("location"),
        "salary_from": payload.get("salary_from"),
        "salary_to": payload.get("salary_to"),
        "currency": payload.get("currency"),
        "experience": payload.get("experience"),
        "employment_type": payload.get("employment_type"),
        "published_at": datetime.fromisoformat(
            payload["published_at"].replace("Z", "+00:00")
        ),
        "skills": payload.get("skills", [])
    }


def transform_vacancies(raw_vacancies: List[Dict]) -> List[Dict]:
    return [transform_vacancy(raw) for raw in raw_vacancies]
