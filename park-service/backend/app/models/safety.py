from sqlalchemy import Column, Integer, String, Text, Date, DateTime
from sqlalchemy.sql import func
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'shared'))
from shared.database.db import Base


class SafetyRecord(Base):
    __tablename__ = 'safety_records'

    id = Column(Integer, primary_key=True)
    enterprise_id = Column(Integer, nullable=False)
    type = Column(String(50), nullable=False)
    incident_date = Column(Date)
    description = Column(Text)
    severity = Column(String(20))
    measures = Column(Text)
    status = Column(String(20), default='pending')
    created_at = Column(DateTime, server_default=func.now())

    def to_dict(self):
        return {
            'id': self.id, 'enterprise_id': self.enterprise_id, 'type': self.type,
            'incident_date': self.incident_date.isoformat() if self.incident_date else None,
            'description': self.description, 'severity': self.severity,
            'measures': self.measures, 'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
