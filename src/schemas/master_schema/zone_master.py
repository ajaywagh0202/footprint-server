from pydantic import BaseModel
from typing import Optional

class ZoneCreate(BaseModel):
    zone : str
    zone_code : str
    headquarter : str
    region : Optional[str] = None

    model_config = {"from_attributes": True}

class ZoneGet(BaseModel):
    id : int
    zone : str
    zone_code : str
    headquarter : str
    region : Optional[str] = None

    model_config = {"from_attributes": True}

class ZoneUpdate(BaseModel):
    zone : Optional[str] = None
    zone_code : Optional[str] = None
    headquarter : Optional[str] = None
    region : Optional[str] = None

    model_config = {"from_attributes": True}
