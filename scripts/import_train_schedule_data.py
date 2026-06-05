from pathlib import Path
import argparse
import sys

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.database import Base, engine, session  # noqa: E402
from src.models.Master.division_master import DivisionMaster  # noqa: E402, F401
from src.models.Master.station_master import StationMaster  # noqa: E402
from src.models.Master.zone_master import ZoneMaster  # noqa: E402, F401
from src.models.Transaction.train_schedule import TrainSchedule  # noqa: E402


DEFAULT_CSV_PATH = PROJECT_ROOT / "sample" / "Train Master Data.csv"

REQUIRED_COLUMNS = [
    "train_no",
    "train_name",
    "islno",
    "station_code",
    "station_name",
    "arrival_time",
    "departure_time",
    "distance",
    "from_station_code",
    "from_station_name",
    "to_station_code",
    "to_station_name",
]
PROPER_CASE_COLUMNS = {
    "train_name",
    "station_name",
    "from_station_name",
    "to_station_name",
}
TEXT_COLUMNS = [
    "train_no",
    "islno",
    "station_code",
    "arrival_time",
    "departure_time",
    "from_station_code",
    "to_station_code",
]
SCHEDULE_KEY_COLUMNS = ["train_no", "islno", "station_code"]


def clean_text(value):
    if pd.isna(value):
        return None
    value = str(value).strip().strip("'").strip('"').strip()
    return value or None


def proper_case(value):
    value = clean_text(value)
    if value is None:
        return None
    return value.title()


def clean_distance(value):
    if pd.isna(value):
        return None
    value = str(value).strip().strip("'").strip('"').strip()
    if not value:
        return None
    return int(float(value))


def load_train_schedule_rows(csv_path):
    data = pd.read_csv(csv_path)
    data.columns = [column.strip().lower().replace(" ", "_") for column in data.columns]

    missing_columns = set(REQUIRED_COLUMNS) - set(data.columns)
    if missing_columns:
        missing = ", ".join(sorted(missing_columns))
        raise ValueError(f"CSV missing required columns: {missing}")

    data = data[REQUIRED_COLUMNS].copy()

    for column in PROPER_CASE_COLUMNS:
        data[column] = data[column].apply(proper_case)

    for column in TEXT_COLUMNS:
        data[column] = data[column].apply(clean_text)

    data["distance"] = data["distance"].apply(clean_distance)
    data = data.dropna(subset=REQUIRED_COLUMNS)
    data = data.drop_duplicates(subset=SCHEDULE_KEY_COLUMNS, keep="first")
    return data.to_dict(orient="records")


def import_train_schedule(csv_path=DEFAULT_CSV_PATH):
    Base.metadata.create_all(bind=engine)
    rows = load_train_schedule_rows(csv_path)

    db = session()
    try:
        existing_schedule_keys = {
            (train_no, islno, station_code)
            for train_no, islno, station_code in db.query(
                TrainSchedule.train_no,
                TrainSchedule.islno,
                TrainSchedule.station_code,
            ).all()
        }
        valid_station_codes = {
            code
            for (code,) in db.query(StationMaster.station_code).all()
            if code is not None
        }

        inserted = 0
        skipped_duplicates = 0
        skipped_missing_station = 0

        for row in rows:
            schedule_key = tuple(row[column] for column in SCHEDULE_KEY_COLUMNS)
            required_station_codes = {
                row["station_code"],
                row["from_station_code"],
                row["to_station_code"],
            }

            if schedule_key in existing_schedule_keys:
                skipped_duplicates += 1
                continue

            if not required_station_codes.issubset(valid_station_codes):
                skipped_missing_station += 1
                continue

            db.add(TrainSchedule(**row))
            existing_schedule_keys.add(schedule_key)
            inserted += 1

        db.commit()
        return {
            "csv_rows_after_cleaning": len(rows),
            "inserted": inserted,
            "skipped_duplicates": skipped_duplicates,
            "skipped_missing_station": skipped_missing_station,
        }
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Import train schedule CSV rows into train_schedule."
    )
    parser.add_argument(
        "csv_path",
        nargs="?",
        default=str(DEFAULT_CSV_PATH),
        help="Path to the train schedule CSV file.",
    )
    args = parser.parse_args()

    result = import_train_schedule(args.csv_path)

    print("Train schedule import completed")
    for key, value in result.items():
        print(f"{key}: {value}")
