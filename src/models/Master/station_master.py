from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from ...database import Base

class StationMaster(Base):
    __tablename__ = "station_master"

    id = Column(Integer, primary_key=True, index=True)
    station = Column(String, nullable=False)
    station_code = Column(String, nullable=False, unique=True, index=True)
    station_category = Column(String, nullable=False)
    district = Column(String, nullable=False)
    state = Column(String, nullable=False)
    division_code = Column(String, ForeignKey("division_master.division_code"), nullable=False, index=True)

    division = relationship("DivisionMaster", back_populates="stations")
    train_schedules = relationship(
        "TrainSchedule",
        foreign_keys="TrainSchedule.station_code",
        back_populates="station",
    )
    train_schedules_from = relationship(
        "TrainSchedule",
        foreign_keys="TrainSchedule.from_station_code",
        back_populates="from_station",
    )
    train_schedules_to = relationship(
        "TrainSchedule",
        foreign_keys="TrainSchedule.to_station_code",
        back_populates="to_station",
    )
