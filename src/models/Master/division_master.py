import uuid
from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from ...database import Base

class DivisionMaster(Base):
    __tablename__ = "division_master"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    division = Column(String, nullable=False)
    division_code = Column(String, nullable=False, unique=True)
    headquarter = Column(String, nullable=False)
    zone_id = Column(UUID(as_uuid=True), ForeignKey("zone_master.id"), nullable=False)

    # Optional: ORM relationship for easy access
    zone = relationship("ZoneMaster", back_populates="divisions")
    stations = relationship("StationMaster", back_populates="division")
