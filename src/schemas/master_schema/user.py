from pydantic import BaseModel
from typing import Optional

class UserCreate(BaseModel):
    username : str
    password : str
    name : str 
    email : str 
    phone : str
    employee_no : str
    user_type : int
    is_active : int

class UserUpdate(BaseModel):
    username : Optional[str] = None
    password : Optional[str] = None
    name : Optional[str] = None
    email : Optional[str] = None
    phone : Optional[str] = None
    employee_no : Optional[str] = None
    user_type : Optional[int] = None
    is_active : Optional[int] = None

class UserOut(BaseModel):
    id : int
    username : str
    name : str
    email : str
    phone : str
    employee_no : str
    user_type : int
    is_active : int
    created_at : str

    model_config = {"from_attributes": True}


class UserLogin(BaseModel):
    username: str
    password: str
