from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, Depends, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import FileResponse, JSONResponse
from sqlalchemy import and_, func
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from starlette.datastructures import UploadFile

from ...database import get_db
from ...models.Master.department import Department
from ...models.Master.department_manual import DepartmentManual
from ...schemas.manual_schema.department_manual import (
    DepartmentGet,
    DepartmentManualGet,
    DepartmentWithManualCount,
)


router = APIRouter(prefix="/api/manuals", tags=["Department Manuals"])

PROJECT_ROOT = Path(__file__).resolve().parents[3]
UPLOAD_BASE_DIR = Path("Data_WareHouse") / "Department_Manuals_Warehouse"
WAREHOUSE_ROOT = PROJECT_ROOT.parent / UPLOAD_BASE_DIR
VERSION_TYPES = {
    "original": "Original",
    "revised": "Revised",
}


def error_response(message: str, status_code: int):
    return JSONResponse(status_code=status_code, content={"error": message})


def success_response(message: str, data, status_code: int = status.HTTP_200_OK):
    return JSONResponse(
        status_code=status_code,
        content=jsonable_encoder({"message": message, "data": data}),
    )


def clean_optional(value):
    if value is None:
        return None
    value = str(value).strip()
    return value or None


def normalize_version_type(value):
    value = clean_optional(value)
    if value is None:
        return None
    return VERSION_TYPES.get(value.lower())


def parse_bool(value):
    value = str(value).strip().lower()
    if value in {"true", "1", "yes"}:
        return True
    if value in {"false", "0", "no"}:
        return False
    return None


def parse_revision_number(value):
    value = clean_optional(value)
    if value is None:
        return None
    try:
        return int(value)
    except ValueError:
        return None


def detect_version_type(file_name: str):
    stem = Path(file_name).stem.strip().lower()
    if stem.endswith("revised"):
        return "Revised"
    if stem.endswith("original"):
        return "Original"
    return None


def manual_file_url(request: Request, manual_id: int):
    return str(request.url_for("open_manual_file", manual_id=manual_id))


def manual_data(manual: DepartmentManual, request: Request):
    data = DepartmentManualGet.model_validate(manual).model_dump()
    data["file_url"] = manual_file_url(request, manual.id)
    return data


def resolve_manual_file_path(manual: DepartmentManual):
    stored_path = Path(manual.file_path)
    candidates = []

    if stored_path.is_absolute():
        candidates.append(stored_path)
    else:
        candidates.append(WAREHOUSE_ROOT / stored_path)
        candidates.append(PROJECT_ROOT / stored_path)
        candidates.append(PROJECT_ROOT.parent / stored_path)

    for candidate in candidates:
        resolved = candidate.resolve()
        if resolved.exists() and resolved.is_file():
            return resolved

    return None


def manual_file_response(manual: DepartmentManual):
    file_path = resolve_manual_file_path(manual)
    if file_path is None:
        return error_response("Manual file not found on disk", status.HTTP_404_NOT_FOUND)

    return FileResponse(
        path=file_path,
        media_type="application/pdf",
        filename=manual.file_name,
        content_disposition_type="inline",
    )


@router.get("/departments")
def get_departments(db: Session = Depends(get_db)):
    rows = (
        db.query(
            Department,
            func.count(DepartmentManual.id).label("active_manuals_count"),
        )
        .outerjoin(
            DepartmentManual,
            and_(
                DepartmentManual.department_code == Department.department_code,
                DepartmentManual.is_active.is_(True),
            ),
        )
        .group_by(
            Department.id,
            Department.department_code,
            Department.department_name,
            Department.created_at,
        )
        .order_by(Department.created_at.desc())
        .all()
    )

    data = [
        DepartmentWithManualCount(
            **DepartmentGet.model_validate(department).model_dump(),
            active_manuals_count=active_manuals_count,
        ).model_dump()
        for department, active_manuals_count in rows
    ]
    return success_response("Departments fetched successfully", data)


@router.get("/departments/list")
def get_departments_list(db: Session = Depends(get_db)):
    departments = db.query(Department).order_by(Department.created_at.desc()).all()
    data = [
        DepartmentGet.model_validate(department).model_dump()
        for department in departments
    ]
    return success_response("Departments fetched successfully", data)


@router.get("/department/{department_code}")
def get_department_manuals(
    request: Request,
    department_code: str,
    version_type: str | None = None,
    is_active: str = "true",
    db: Session = Depends(get_db),
):
    active_filter = parse_bool(is_active)
    if active_filter is None:
        return error_response(
            "is_active must be true or false",
            status.HTTP_400_BAD_REQUEST,
        )

    normalized_version_type = None
    if version_type is not None:
        normalized_version_type = normalize_version_type(version_type)
        if normalized_version_type is None:
            return error_response(
                "version_type must be Original or Revised",
                status.HTTP_400_BAD_REQUEST,
            )

    department = (
        db.query(Department)
        .filter(func.lower(Department.department_code) == department_code.lower())
        .first()
    )
    if not department:
        return error_response("Department not found", status.HTTP_404_NOT_FOUND)

    manuals_query = db.query(DepartmentManual).filter(
        DepartmentManual.department_code == department.department_code,
        DepartmentManual.is_active.is_(active_filter),
    )
    if normalized_version_type:
        manuals_query = manuals_query.filter(
            DepartmentManual.version_type == normalized_version_type
        )

    manuals = manuals_query.order_by(DepartmentManual.created_at.desc()).all()
    data = {
        **DepartmentGet.model_validate(department).model_dump(),
        "manuals": [manual_data(manual, request) for manual in manuals],
    }
    return success_response("Department manuals fetched successfully", data)


@router.post("/upload")
async def upload_manual(request: Request, db: Session = Depends(get_db)):
    content_type = request.headers.get("content-type", "").lower()
    upload_file = None
    uploaded_by = None
    is_file_upload = content_type.startswith("multipart/form-data")

    if is_file_upload:
        try:
            form = await request.form()
        except Exception:
            return error_response(
                "Invalid multipart form data. Ensure python-multipart is installed.",
                status.HTTP_400_BAD_REQUEST,
            )

        # Multipart keeps the real PDF upload flow for UI upload buttons.
        department_code = clean_optional(form.get("department_code"))
        display_title = clean_optional(form.get("display_title"))
        version_type = normalize_version_type(form.get("version_type"))
        revision_number_input = form.get("revision_number")
        revision_number = parse_revision_number(revision_number_input)
        description = clean_optional(form.get("description"))
        uploaded_by = clean_optional(form.get("uploaded_by"))
        upload_file = form.get("file")
    else:
        try:
            payload = await request.json()
        except Exception:
            return error_response(
                "Invalid JSON body",
                status.HTTP_400_BAD_REQUEST,
            )

        if not isinstance(payload, dict):
            return error_response("Invalid JSON body", status.HTTP_400_BAD_REQUEST)

        # JSON requests create metadata only; no physical PDF is uploaded.
        department_code = clean_optional(payload.get("department_code"))
        display_title = clean_optional(payload.get("display_title"))
        version_type = normalize_version_type(payload.get("version_type"))
        revision_number_input = payload.get("revision_number")
        revision_number = parse_revision_number(revision_number_input)
        description = clean_optional(payload.get("description"))

    if not department_code:
        return error_response("department_code is required", status.HTTP_400_BAD_REQUEST)
    if not display_title:
        return error_response("display_title is required", status.HTTP_400_BAD_REQUEST)
    if version_type is None:
        return error_response(
            "version_type must be Original or Revised",
            status.HTTP_400_BAD_REQUEST,
        )
    if clean_optional(revision_number_input) is not None and revision_number is None:
        return error_response(
            "revision_number must be an integer",
            status.HTTP_400_BAD_REQUEST,
        )

    if version_type == "Original":
        revision_number = None

    if is_file_upload:
        if not isinstance(upload_file, UploadFile):
            return error_response("file is required", status.HTTP_400_BAD_REQUEST)

        file_name = Path(upload_file.filename or "").name
        if not file_name:
            return error_response("file name is required", status.HTTP_400_BAD_REQUEST)
        if Path(file_name).suffix.lower() != ".pdf":
            return error_response("Only .pdf files are allowed", status.HTTP_400_BAD_REQUEST)

        detected_version_type = detect_version_type(file_name)
        if detected_version_type is None:
            return error_response(
                "PDF file name must end with Original or Revised before .pdf",
                status.HTTP_400_BAD_REQUEST,
            )
        if detected_version_type != version_type:
            return error_response(
                "version_type must match the PDF file name",
                status.HTTP_400_BAD_REQUEST,
            )

    department = (
        db.query(Department)
        .filter(func.lower(Department.department_code) == department_code.lower())
        .first()
    )
    if not department:
        return error_response("Department not found", status.HTTP_404_NOT_FOUND)

    if not is_file_upload:
        # Metadata-only requests generate the file name from title and version.
        file_name = f"{display_title.replace(' ', '_')}_{version_type}.pdf"
    file_path = f"{department.department_code}/{file_name}"
    absolute_path = WAREHOUSE_ROOT / department.department_code / file_name

    duplicate_manual = (
        db.query(DepartmentManual)
        .filter(
            DepartmentManual.department_code == department.department_code,
            DepartmentManual.file_name == file_name,
        )
        .first()
    )
    if duplicate_manual:
        return error_response(
            "A manual with this title and version already exists for this department",
            status.HTTP_409_CONFLICT,
        )

    if is_file_upload and absolute_path.exists():
        return error_response(
            "File already exists for this department",
            status.HTTP_409_CONFLICT,
        )

    try:
        if is_file_upload:
            # Save the real PDF into the matching department warehouse folder.
            absolute_path.parent.mkdir(parents=True, exist_ok=True)
            with absolute_path.open("wb") as buffer:
                while chunk := await upload_file.read(1024 * 1024):
                    buffer.write(chunk)

        manual = DepartmentManual(
            department_code=department.department_code,
            file_name=file_name,
            display_title=display_title,
            version_type=version_type,
            revision_number=revision_number,
            description=description,
            file_path=file_path,
            file_size_kb=(
                (absolute_path.stat().st_size + 1023) // 1024
                if is_file_upload
                else None
            ),
            uploaded_by=uploaded_by,
            is_active=True,
        )
        db.add(manual)
        db.flush()
        data = manual_data(manual, request)
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        if is_file_upload and absolute_path.exists():
            absolute_path.unlink()
        return error_response(
            "Failed to save manual record",
            status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
    except Exception:
        db.rollback()
        if is_file_upload and absolute_path.exists():
            absolute_path.unlink()
        return error_response(
            "Failed to upload manual",
            status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
    finally:
        if is_file_upload and isinstance(upload_file, UploadFile):
            try:
                await upload_file.close()
            except Exception:
                pass

    return success_response(
        "Manual uploaded successfully",
        data,
        status.HTTP_201_CREATED,
    )


@router.get("/{manual_id}/file")
def open_manual_file(manual_id: int, db: Session = Depends(get_db)):
    manual = (
        db.query(DepartmentManual)
        .filter(
            DepartmentManual.id == manual_id,
            DepartmentManual.is_active.is_(True),
        )
        .first()
    )
    if not manual:
        return error_response("Manual not found", status.HTTP_404_NOT_FOUND)

    return manual_file_response(manual)


@router.get("/files/{department_code}/{file_name}")
def open_manual_file_by_path(
    department_code: str,
    file_name: str,
    db: Session = Depends(get_db),
):
    file_name = Path(file_name).name
    manual = (
        db.query(DepartmentManual)
        .filter(
            func.lower(DepartmentManual.department_code) == department_code.lower(),
            DepartmentManual.file_name == file_name,
            DepartmentManual.is_active.is_(True),
        )
        .first()
    )
    if not manual:
        return error_response("Manual not found", status.HTTP_404_NOT_FOUND)

    return manual_file_response(manual)


@router.delete("/{manual_id}")
def deactivate_manual(manual_id: int, db: Session = Depends(get_db)):
    manual = db.query(DepartmentManual).filter(DepartmentManual.id == manual_id).first()
    if not manual:
        return error_response("Manual not found", status.HTTP_404_NOT_FOUND)

    manual.is_active = False
    manual.updated_at = datetime.utcnow()
    try:
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        return error_response(
            "Failed to deactivate manual",
            status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    return success_response(
        "Manual deactivated successfully",
        {"manual_id": manual.id, "is_active": manual.is_active},
    )
