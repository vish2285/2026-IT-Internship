from sqlalchemy import Column, Integer, String, Text, Date, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from datetime import datetime

Base = declarative_base()

class Internship(Base):
    __tablename__ = "internships"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    company = Column(String(255), nullable=False, index=True)
    location = Column(String(255), nullable=False)
    field = Column(String(50), nullable=False, index=True)  # Cybersecurity, IT, Neuroscience
    apply_url = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    posted_date = Column(Date, nullable=False, default=datetime.now().date())
    deadline = Column(Date, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    application_status = Column(String(20), default="not_applied", nullable=False)  # not_applied, applied, started, completed
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "company": self.company,
            "location": self.location,
            "field": self.field,
            "apply_url": self.apply_url,
            "description": self.description,
            "posted_date": self.posted_date.isoformat() if self.posted_date else None,
            "deadline": self.deadline.isoformat() if self.deadline else None,
            "is_active": self.is_active,
            "application_status": self.application_status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
