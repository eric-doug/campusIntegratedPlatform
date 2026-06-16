from sqlalchemy import Column, Integer, String, Numeric, Boolean, Date, DateTime, UniqueConstraint
from sqlalchemy.sql import func
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'shared'))
from shared.database.db import Base


class EnergyConsumption(Base):
    __tablename__ = 'energy_consumption'
    __table_args__ = (UniqueConstraint('enterprise_id', 'type', 'period'),)

    id = Column(Integer, primary_key=True)
    enterprise_id = Column(Integer, nullable=False)
    type = Column(String(30), nullable=False)
    period = Column(Date, nullable=False)
    value = Column(Numeric(12, 2), nullable=False)
    unit = Column(String(20))
    reported = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())

    def to_dict(self):
        return {
            'id': self.id, 'enterprise_id': self.enterprise_id, 'type': self.type,
            'period': self.period.isoformat() if self.period else None,
            'value': float(self.value) if self.value else None,
            'unit': self.unit, 'reported': self.reported,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
