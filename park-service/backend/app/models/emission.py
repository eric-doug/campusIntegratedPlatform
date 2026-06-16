from sqlalchemy import Column, Integer, String, Numeric, Boolean, Date, DateTime, UniqueConstraint
from sqlalchemy.sql import func
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'shared'))
from shared.database.db import Base


class EmissionRecord(Base):
    __tablename__ = 'emission_records'
    __table_args__ = (UniqueConstraint('enterprise_id', 'type', 'period'),)

    id = Column(Integer, primary_key=True)
    enterprise_id = Column(Integer, nullable=False)
    type = Column(String(50), nullable=False)
    period = Column(Date, nullable=False)
    value = Column(Numeric(12, 2), nullable=False)
    limit_value = Column(Numeric(12, 2))
    unit = Column(String(20))
    is_exceeding = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())

    def to_dict(self):
        return {
            'id': self.id, 'enterprise_id': self.enterprise_id, 'type': self.type,
            'period': self.period.isoformat() if self.period else None,
            'value': float(self.value) if self.value else None,
            'limit_value': float(self.limit_value) if self.limit_value else None,
            'unit': self.unit, 'is_exceeding': self.is_exceeding,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
