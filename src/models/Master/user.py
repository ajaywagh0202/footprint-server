from ...database import Base
from sqlalchemy import Column,String,Integer


class User(Base):

    __tablename__ = "users"

    id = Column(Integer,primary_key=True,index=True)
    name = Column(String,nullable=False)
    username = Column(String,nullable=False,unique=True)
    password = Column(String,nullable=False)
    phone = Column(String,nullable=False)
    email = Column(String,nullable=False,unique=True)
    employee_no = Column(String,nullable=False,unique=True)
    user_type = Column(Integer,nullable=False, default=1) # 0 for admin, 1 for regular user
    is_active = Column(Integer,nullable=False, default=1) # 0 for inactive, 1 for active
    created_at = Column(String,nullable=False)

    