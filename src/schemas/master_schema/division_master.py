from pydantic import BaseModel
from typing import Optional
from uuid import UUID

class DivisionCreate(BaseModel):
    division : str
    division_code : str
    headquarter : str
    zone_id : UUID

class DivisionGet(BaseModel):
    id : UUID
    division : str
    division_code : str
    headquarter : str
    zone_id : UUID

    model_config = {"from_attributes": True}


class DivisionWithZone(DivisionGet):
    zone_name : str
    zone_code : str


class DivisionUpdate(BaseModel):
    division : Optional[str] = None
    division_code : Optional[str] = None
    headquarter : Optional[str] = None
    zone_id : Optional[UUID] = None

    model_config = {"from_attributes": True}
