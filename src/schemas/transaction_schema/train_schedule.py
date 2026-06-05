from pydantic import BaseModel
from typing import Optional


class TrainScheduleCreate(BaseModel):
    train_no : str
    train_name : str
    station_code : str
    arrival_time : str
    departure_time : str
    distance : int
    from_station_code : str
    to_station_code : str
    islno : str
    from_station_name : Optional[str] = None
    to_station_name : Optional[str] = None
    station_name : Optional[str] = None

class TrainScheduleGet(BaseModel):
    id : int
    train_no : str
    train_name : str
    station_code : str
    arrival_time : str
    departure_time : str
    distance : int
    from_station_code : str
    to_station_code : str
    islno : str
    station_name : Optional[str] = None
    from_station_name : Optional[str] = None
    to_station_name : Optional[str] = None


    model_config = {"from_attributes": True}

class TrainScheduleUpdate(BaseModel):
    train_no : Optional[str] = None
    train_name : Optional[str] = None
    station_code : Optional[str] = None
    arrival_time : Optional[str] = None
    departure_time : Optional[str] = None
    distance : Optional[int] = None
    from_station_code : Optional[str] = None
    to_station_code : Optional[str] = None

    model_config = {"from_attributes": True}
