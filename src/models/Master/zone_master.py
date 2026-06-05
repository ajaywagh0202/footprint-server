from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import relationship
from ...database import Base

class ZoneMaster(Base):
    __tablename__ = "zone_master"

    id = Column(Integer, primary_key=True, index=True)
    zone = Column(String, nullable=False)
    zone_code = Column(String, nullable=False, unique=True, index=True)
    headquarter = Column(String, nullable=False)
    region = Column(String, nullable=True)

    divisions = relationship("DivisionMaster", back_populates="zone")
