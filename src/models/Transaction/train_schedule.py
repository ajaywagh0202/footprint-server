import uuid
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from ...database import Base

class TrainSchedule(Base):
    __tablename__ = "train_schedule"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    train_no = Column(String, nullable=False)
    train_name = Column(String, nullable=False)
    station_code = Column(String,nullable=True )
    station_uid = Column(UUID(as_uuid=True), ForeignKey("station_master.id"), nullable=False)
    arrival_time = Column(String, nullable=False)
    departure_time = Column(String, nullable=False)
    distance = Column(Integer, nullable=False)
    from_station_code = Column(String, nullable=False)
    to_station_code = Column(String, nullable=False)
    from_station_uid = Column(UUID(as_uuid=True), ForeignKey("station_master.id"), nullable=False)
    to_station_uid = Column(UUID(as_uuid=True), ForeignKey("station_master.id"), nullable=False)

    # Optional: ORM relationship for easy access
    station = relationship("StationMaster", foreign_keys=[station_uid], back_populates="train_schedules")
    from_station = relationship("StationMaster", foreign_keys=[from_station_uid], back_populates="train_schedules_from")
    to_station = relationship("StationMaster", foreign_keys=[to_station_uid], back_populates="train_schedules_to")

    
