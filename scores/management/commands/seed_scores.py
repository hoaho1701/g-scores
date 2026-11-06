"""Load the exam CSV into the database.

Usage: ``python manage.py seed_scores [--file PATH] [--batch SIZE]``
"""

import csv

from django.core.management.base import BaseCommand

from scores.models import StudentScore

# CSV columns holding a score; they share their names with the model fields.
SCORE_COLUMNS = [
    "toan",
    "ngu_van",
    "ngoai_ngu",
    "vat_li",
    "hoa_hoc",
    "sinh_hoc",
    "lich_su",
    "dia_li",
    "gdcd",
]


def to_float(value):
    """Convert a CSV cell to float; an empty cell becomes None (stored as NULL)."""
    if value.strip() == "":
        return None
    return float(value)


def parse_row(row):
    """Build an unsaved StudentScore from one CSV row."""
    data = {
        "sbd": row["sbd"],  # keep as text to preserve leading zeros
        "ma_ngoai_ngu": row["ma_ngoai_ngu"] or None,
    }
    for col in SCORE_COLUMNS:
        data[col] = to_float(row[col])
    return StudentScore(**data)


class Command(BaseCommand):
    help = "Import dataset into the database"

    def add_arguments(self, parser):
        parser.add_argument("--file", default="dataset/diem_thi_thpt_2024.csv")
        parser.add_argument("--batch", type=int, default=5000)

    def handle(self, *args, **options):
        path = options["file"]
        batch_size = options["batch"]

        # Start empty so re-running gives the same result (sbd is unique).
        StudentScore.objects.all().delete()

        batch = []
        total = 0

        # Stream the file and insert in batches: bounded memory, few SQL statements.
        with open(path, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                batch.append(parse_row(row))

                if len(batch) >= batch_size:
                    StudentScore.objects.bulk_create(batch)
                    total += len(batch)  # count before the batch is emptied
                    batch = []
                    self.stdout.write(f"{total} rows")

        # The last batch is usually smaller than batch_size.
        if batch:
            StudentScore.objects.bulk_create(batch)
            total += len(batch)

        self.stdout.write(self.style.SUCCESS(f"Done: {total}"))
