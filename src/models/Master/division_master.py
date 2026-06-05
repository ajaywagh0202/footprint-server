from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from ...database import Base

class DivisionMaster(Base):
    __tablename__ = "division_master"

    id = Column(Integer, primary_key=True, index=True)
    division = Column(String, nullable=False)
    division_code = Column(String, nullable=False, unique=True, index=True)
    headquarter = Column(String, nullable=False)
    zone_code = Column(String, ForeignKey("zone_master.zone_code"), nullable=False, index=True)

    zone = relationship("ZoneMaster", back_populates="divisions")
    stations = relationship("StationMaster", back_populates="division")
