from pydantic import BaseModel
from typing import Optional
from uuid import UUID


class StationCreate(BaseModel):
    station : str
    station_code : str
    station_type : str
    station_category : str
    district : str
    state : str
    division_id : UUID

class StationGet(BaseModel):
    id : UUID
    station : str
    station_code : str
    station_type : str
    station_category : str
    district : str
    state : str
    division_id : UUID

    model_config = {"from_attributes": True}

class StationUpdate(BaseModel):
    station : Optional[str] = None
    station_code : Optional[str] = None
    station_type : Optional[str] = None
    station_category : Optional[str] = None
    district : Optional[str] = None
    state : Optional[str] = None
    division_id : Optional[UUID] = None

    model_config = {"from_attributes": True}
