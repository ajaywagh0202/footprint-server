import uuid
from sqlalchemy import Column, String, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from ...database import Base

class ZoneMaster(Base):
    __tablename__ = "zone_master"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    zone = Column(String, nullable=False)
    zone_code = Column(String, nullable=False, unique=True)
    headquarter = Column(String, nullable=False)
    region = Column(String, nullable=True)

    divisions = relationship("DivisionMaster", back_populates="zone")
