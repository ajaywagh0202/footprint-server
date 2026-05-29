from pydantic import BaseModel
from typing import Optional
from uuid import UUID


class TrainScheduleCreate(BaseModel):
    train_no : str
    train_name : str
    station_code : Optional[str] = None
    station_uid : UUID
    arrival_time : str
    departure_time : str
    distance : int
    from_station_code : str
    to_station_code : str
    from_station_uid : UUID
    to_station_uid : UUID

class TrainScheduleGet(BaseModel):
    id : UUID
    train_no : str
    train_name : str
    station_code : Optional[str] = None
    station_uid : UUID
    arrival_time : str
    departure_time : str
    distance : int
    from_station_code : str
    to_station_code : str
    from_station_uid : UUID
    to_station_uid : UUID

    model_config = {"from_attributes": True}

class TrainScheduleUpdate(BaseModel):
    train_no : Optional[str] = None
    train_name : Optional[str] = None
    station_code : Optional[str] = None
    station_uid : Optional[UUID] = None
    arrival_time : Optional[str] = None
    departure_time : Optional[str] = None
    distance : Optional[int] = None
    from_station_code : Optional[str] = None
    to_station_code : Optional[str] = None
    from_station_uid : Optional[UUID] = None
    to_station_uid : Optional[UUID] = None

    model_config = {"from_attributes": True}
