from pathlib import Path
import argparse
import sys

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.database import Base, engine, session  # noqa: E402
from src.models.Master.division_master import DivisionMaster  # noqa: E402
from src.models.Master.station_master import StationMaster  # noqa: E402
from src.models.Master.zone_master import ZoneMaster  # noqa: E402, F401
from src.models.Transaction.train_schedule import TrainSchedule  # noqa: E402, F401


DEFAULT_CSV_PATH = (
    r"C:\Users\USER\Downloads\New folder"
    r"\Railway_station_zone-category_wise_list_updated.csv"
)

REQUIRED_COLUMNS = [
    "station",
    "station_code",
    "station_category",
    "division_code",
    "district",
    "state",
]
PROPER_CASE_COLUMNS = {"station", "district", "state"}
UNCHANGED_TEXT_COLUMNS = {"station_code", "station_category", "division_code"}


def proper_case(value):
    if pd.isna(value):
        return None
    value = str(value).strip()
    if not value:
        return None
    return value.title()


def clean_unchanged(value):
    if pd.isna(value):
        return None
    value = str(value).strip()
    return value or None


def load_station_rows(csv_path):
    data = pd.read_csv(csv_path)
    data.columns = [column.strip().lower().replace(" ", "_") for column in data.columns]

    missing_columns = set(REQUIRED_COLUMNS) - set(data.columns)
    if missing_columns:
        missing = ", ".join(sorted(missing_columns))
        raise ValueError(f"CSV missing required columns: {missing}")

    data = data[REQUIRED_COLUMNS].copy()

    for column in PROPER_CASE_COLUMNS:
        data[column] = data[column].apply(proper_case)

    for column in UNCHANGED_TEXT_COLUMNS:
        data[column] = data[column].apply(clean_unchanged)

    data = data.dropna(subset=REQUIRED_COLUMNS)
    data = data.drop_duplicates(subset=["station_code"], keep="first")
    return data.to_dict(orient="records")


def import_station_master(csv_path=DEFAULT_CSV_PATH):
    Base.metadata.create_all(bind=engine)
    rows = load_station_rows(csv_path)

    db = session()
    try:
        existing_station_codes = {
            code
            for (code,) in db.query(StationMaster.station_code).all()
            if code is not None
        }
        valid_division_codes = {
            code
            for (code,) in db.query(DivisionMaster.division_code).all()
            if code is not None
        }

        inserted = 0
        skipped_duplicates = 0
        skipped_missing_division = 0

        for row in rows:
            station_code = row["station_code"]
            division_code = row["division_code"]

            if station_code in existing_station_codes:
                skipped_duplicates += 1
                continue

            if division_code not in valid_division_codes:
                skipped_missing_division += 1
                continue

            db.add(StationMaster(**row))
            existing_station_codes.add(station_code)
            inserted += 1

        db.commit()
        return {
            "csv_rows_after_cleaning": len(rows),
            "inserted": inserted,
            "skipped_duplicates": skipped_duplicates,
            "skipped_missing_division": skipped_missing_division,
        }
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Import railway station CSV rows into station_master."
    )
    parser.add_argument(
        "csv_path",
        nargs="?",
        default=DEFAULT_CSV_PATH,
        help="Path to the station CSV file.",
    )
    args = parser.parse_args()

    result = import_station_master(args.csv_path)

    print("Station master import completed")
    for key, value in result.items():
        print(f"{key}: {value}")
