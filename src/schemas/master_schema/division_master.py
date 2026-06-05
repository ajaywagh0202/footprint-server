from pydantic import BaseModel
from typing import Optional

class DivisionCreate(BaseModel):
    division : str
    division_code : str
    headquarter : str
    zone_code : str

class DivisionGet(BaseModel):
    id : int
    division : str
    division_code : str
    headquarter : str
    zone_code : str

    model_config = {"from_attributes": True}


class DivisionWithZone(DivisionGet):
    zone_name : str


class DivisionUpdate(BaseModel):
    division : Optional[str] = None
    division_code : Optional[str] = None
    headquarter : Optional[str] = None
    zone_code : Optional[str] = None

    model_config = {"from_attributes": True}
