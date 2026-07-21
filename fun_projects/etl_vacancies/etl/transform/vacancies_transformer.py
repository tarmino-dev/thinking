from datetime import datetime
from typing import List, Dict, Optional, Tuple


def parse_published_at(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


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
        "published_at": parse_published_at(payload.get("published_at")),
        "skills": payload.get("skills", []),
    }


def transform_vacancies(
    raw_vacancies: List[Dict],
) -> Tuple[List[Dict], List[Dict]]:
    valid: List[Dict] = []
    rejected: List[Dict] = []

    for raw in raw_vacancies:
        try:
            valid.append(transform_vacancy(raw))
        except (KeyError, ValueError, TypeError) as error:
            rejected.append({"id": raw.get("id"), "reason": str(error)})

    return valid, rejected
