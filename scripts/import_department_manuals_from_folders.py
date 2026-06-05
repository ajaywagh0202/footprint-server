from datetime import datetime
from pathlib import Path
import argparse
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.database import Base, engine, session  # noqa: E402
from src.models.Master.department import Department  # noqa: E402
from src.models.Master.department_manual import DepartmentManual  # noqa: E402


DEFAULT_BASE_DIRECTORY = Path(
    r"D:\AJAY WAGH JE IT\WORK_PROJECT\MASTER_SERVER"
    r"\Data_WareHouse\Department_Manuals_Warehouse"
)
UPLOADED_BY = "system_import"


def detect_version_type(file_name):
    stem = Path(file_name).stem
    parts = stem.split("_")
    if not parts:
        return None

    last_segment = parts[-1].strip().lower()
    if last_segment == "original":
        return "Original"
    if last_segment == "revised":
        return "Revised"
    return None


def build_display_title(file_name):
    stem = Path(file_name).stem
    parts = stem.split("_")
    title_parts = parts[:-1]
    return " ".join(part.strip() for part in title_parts if part.strip()).strip()


def get_file_size_kb(file_path):
    return (file_path.stat().st_size + 1023) // 1024


def load_department_codes(db):
    return {
        code
        for (code,) in db.query(Department.department_code).all()
        if code is not None
    }


def manual_exists(db, department_code, file_name):
    return (
        db.query(DepartmentManual)
        .filter(
            DepartmentManual.department_code == department_code,
            DepartmentManual.file_name == file_name,
        )
        .first()
        is not None
    )


def build_manual(department_code, pdf_path):
    file_name = pdf_path.name
    version_type = detect_version_type(file_name)
    now = datetime.utcnow()

    return DepartmentManual(
        department_code=department_code,
        file_name=file_name,
        display_title=build_display_title(file_name),
        version_type=version_type,
        revision_number=None,
        description=None,
        file_path=f"{department_code}/{file_name}",
        file_size_kb=get_file_size_kb(pdf_path),
        uploaded_by=UPLOADED_BY,
        is_active=True,
        created_at=now,
        updated_at=now,
    )


def import_department_manuals(base_directory=DEFAULT_BASE_DIRECTORY):
    base_directory = Path(base_directory)
    if not base_directory.exists():
        raise RuntimeError(f"Base directory not found: {base_directory}")
    if not base_directory.is_dir():
        raise RuntimeError(f"Base path is not a directory: {base_directory}")

    Base.metadata.create_all(bind=engine)

    total_pdfs = 0
    inserted = 0
    skipped_duplicate = 0
    skipped_no_keyword = 0
    skipped_unknown_dept = 0

    db = session()
    try:
        department_codes = load_department_codes(db)

        for department_folder in sorted(base_directory.iterdir()):
            if not department_folder.is_dir():
                continue

            department_code = department_folder.name
            if department_code not in department_codes:
                print(
                    f"SKIPPED FOLDER: {department_code} -> "
                    "not found in departments table"
                )
                skipped_unknown_dept += 1
                continue

            print(f"Scanning: {department_code} folder...")

            for pdf_path in sorted(department_folder.iterdir()):
                if not pdf_path.is_file() or pdf_path.suffix.lower() != ".pdf":
                    continue

                total_pdfs += 1
                file_name = pdf_path.name
                version_type = detect_version_type(file_name)

                if version_type is None:
                    print(
                        f"SKIPPED: {file_name} -> "
                        "no Original/Revised keyword at end of filename"
                    )
                    skipped_no_keyword += 1
                    continue

                try:
                    if manual_exists(db, department_code, file_name):
                        print(f"SKIPPED DUPLICATE: {file_name} -> {department_code}")
                        skipped_duplicate += 1
                        continue

                    db.add(build_manual(department_code, pdf_path))
                    db.commit()
                    print(f"INSERTED: {file_name} [{version_type}] -> {department_code}")
                    inserted += 1
                except Exception as exc:
                    db.rollback()
                    print(f"ERROR: {file_name} -> {department_code}: {exc}")
    finally:
        db.close()

    print("======= IMPORT COMPLETE =======")
    print(f"Total PDFs found     : {total_pdfs}")
    print(f"Successfully inserted: {inserted}")
    print(f"Skipped (duplicate) : {skipped_duplicate}")
    print(f"Skipped (no keyword): {skipped_no_keyword}")
    print(f"Skipped (unknown dept): {skipped_unknown_dept}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Import department manual PDFs into department_manuals."
    )
    parser.add_argument(
        "base_directory",
        nargs="?",
        default=str(DEFAULT_BASE_DIRECTORY),
        help="Base directory containing department PDF folders.",
    )
    args = parser.parse_args()

    import_department_manuals(args.base_directory)
