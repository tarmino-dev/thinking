import unittest
from datetime import datetime, timezone

from etl.transform.vacancies_transformer import transform_vacancies


class TransformVacanciesTest(unittest.TestCase):
    def test_invalid_record_does_not_break_batch(self):
        raw_vacancies = [
            {
                "id": "vac_ok",
                "payload": {
                    "title": "Python Developer",
                    "published_at": "2024-01-10T09:30:00Z",
                    "skills": ["Python"],
                },
            },
            {
                "id": "vac_bad_date",
                "payload": {"title": "Broken", "published_at": "not-a-date"},
            },
        ]

        valid, rejected = transform_vacancies(raw_vacancies)

        # The valid record still reaches the result.
        self.assertEqual(len(valid), 1)
        self.assertEqual(valid[0]["id"], "vac_ok")
        self.assertEqual(
            valid[0]["published_at"],
            datetime(2024, 1, 10, 9, 30, tzinfo=timezone.utc),
        )

        # The bad record is collected instead of raising.
        self.assertEqual(len(rejected), 1)
        self.assertEqual(rejected[0]["id"], "vac_bad_date")
        self.assertIn("reason", rejected[0])

    def test_missing_published_at_is_kept_as_none(self):
        raw_vacancies = [
            {"id": "vac_no_date", "payload": {"title": "No date"}},
        ]

        valid, rejected = transform_vacancies(raw_vacancies)

        self.assertEqual(rejected, [])
        self.assertEqual(len(valid), 1)
        self.assertIsNone(valid[0]["published_at"])


if __name__ == "__main__":
    unittest.main()
