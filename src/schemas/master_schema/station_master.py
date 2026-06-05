from pydantic import BaseModel
from typing import Optional


class StationCreate(BaseModel):
    station : str
    station_code : str
    station_type : str
    station_category : str
    district : str
    state : str
    division_code : str

class StationGet(BaseModel):
    id : int
    station : str
    station_code : str
    station_type : Optional[str] = None
    station_category : str
    district : str
    state : str
    division_code : str

    model_config = {"from_attributes": True}


class StationWithDivisionZone(StationGet):
    division_name : str
    zone_name : str
    zone_code : str


class StationUpdate(BaseModel):
    station : Optional[str] = None
    station_code : Optional[str] = None
    station_type : Optional[str] = None
    station_category : Optional[str] = None
    district : Optional[str] = None
    state : Optional[str] = None
    division_code : Optional[str] = None

    model_config = {"from_attributes": True}
