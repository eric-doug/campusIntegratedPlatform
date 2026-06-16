from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'shared'))
from shared.database.db import Base


class Submission(Base):
    __tablename__ = 'submissions'

    id = Column(Integer, primary_key=True)
    form_id = Column(Integer, nullable=False)
    department = Column(String(100), nullable=False)
    status = Column(String(20), default='submitted')
    submitted_at = Column(DateTime, server_default=func.now())
    feedback = Column(Text)
    reviewed_at = Column(DateTime)

    def to_dict(self):
        return {
            'id': self.id, 'form_id': self.form_id, 'department': self.department,
            'status': self.status,
            'submitted_at': self.submitted_at.isoformat() if self.submitted_at else None,
            'feedback': self.feedback,
            'reviewed_at': self.reviewed_at.isoformat() if self.reviewed_at else None,
        }
