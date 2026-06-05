from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class DepartmentGet(BaseModel):
    id: int
    department_code: str
    department_name: str
    created_at: datetime

    model_config = {"from_attributes": True}


class DepartmentWithManualCount(DepartmentGet):
    active_manuals_count: int


class DepartmentManualGet(BaseModel):
    id: int
    department_code: str
    file_name: str
    display_title: str
    version_type: str
    revision_number: Optional[int] = None
    description: Optional[str] = None
    file_path: str
    file_size_kb: Optional[int] = None
    uploaded_by: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime
    file_url: Optional[str] = None

    model_config = {"from_attributes": True}


class DepartmentWithManuals(DepartmentGet):
    manuals: list[DepartmentManualGet]
