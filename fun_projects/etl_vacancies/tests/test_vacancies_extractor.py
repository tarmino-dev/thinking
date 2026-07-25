import unittest
from datetime import date

from etl.extract.vacancies_extractor import source_filename


class SourceFilenameTest(unittest.TestCase):
    def test_builds_filename_from_date(self):
        self.assertEqual(
            source_filename(date(2024, 1, 10)),
            "vacancies_2024_01_10.json",
        )

    def test_zero_pads_month_and_day(self):
        self.assertEqual(
            source_filename(date(2024, 3, 5)),
            "vacancies_2024_03_05.json",
        )


if __name__ == "__main__":
    unittest.main()
