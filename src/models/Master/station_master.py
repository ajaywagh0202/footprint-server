import uuid
from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from ...database import Base

class StationMaster(Base):
    __tablename__ = "station_master"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    station = Column(String, nullable=False)
    station_code = Column(String, nullable=False, unique=True)
    station_type = Column(String, nullable=False)
    station_category = Column(String, nullable=False)
    district = Column(String, nullable=False)
    state = Column(String, nullable=False)
    division_id = Column(UUID(as_uuid=True), ForeignKey("division_master.id"), nullable=False)

    # Optional: ORM relationship for easy access
    division = relationship("DivisionMaster", back_populates="stations")
    train_schedules = relationship(
        "TrainSchedule",
        foreign_keys="TrainSchedule.station_uid",
        back_populates="station",
    )
    train_schedules_from = relationship(
        "TrainSchedule",
        foreign_keys="TrainSchedule.from_station_uid",
        back_populates="from_station",
    )
    train_schedules_to = relationship(
        "TrainSchedule",
        foreign_keys="TrainSchedule.to_station_uid",
        back_populates="to_station",
    )
