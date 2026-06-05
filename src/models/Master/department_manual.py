from datetime import datetime

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from ...database import Base


class DepartmentManual(Base):
    __tablename__ = "department_manuals"
    __table_args__ = (
        CheckConstraint(
            "version_type IN ('Original', 'Revised')",
            name="ck_department_manuals_version_type",
        ),
    )

    id = Column(Integer, primary_key=True, index=True)
    department_code = Column(
        String(60),
        ForeignKey("departments.department_code"),
        nullable=False,
        index=True,
    )
    file_name = Column(String(300), nullable=False)
    display_title = Column(String(300), nullable=False)
    version_type = Column(String(10), nullable=False)
    revision_number = Column(Integer, nullable=True)
    description = Column(Text, nullable=True)
    file_path = Column(String(500), nullable=False)
    file_size_kb = Column(Integer, nullable=True)
    uploaded_by = Column(String(120), nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    department = relationship("Department", back_populates="manuals")
