from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from ...database import Base

class TrainSchedule(Base):
    __tablename__ = "train_schedule"

    id = Column(Integer, primary_key=True, index=True)
    train_no = Column(String, nullable=False)
    train_name = Column(String, nullable=False)
    islno = Column(String, nullable=False)
    station_name = Column(String, nullable=False)
    station_code = Column(String, ForeignKey("station_master.station_code"), nullable=False, index=True)
    arrival_time = Column(String, nullable=False)
    departure_time = Column(String, nullable=False)
    distance = Column(Integer, nullable=False)
    from_station_name = Column(String, nullable=False)
    from_station_code = Column(String, ForeignKey("station_master.station_code"), nullable=False, index=True)
    to_station_name = Column(String, nullable=False)
    to_station_code = Column(String, ForeignKey("station_master.station_code"), nullable=False, index=True)

    station = relationship("StationMaster", foreign_keys=[station_code], back_populates="train_schedules")
    from_station = relationship("StationMaster", foreign_keys=[from_station_code], back_populates="train_schedules_from")
    to_station = relationship("StationMaster", foreign_keys=[to_station_code], back_populates="train_schedules_to")

    
