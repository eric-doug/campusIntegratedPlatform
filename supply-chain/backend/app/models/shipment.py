from sqlalchemy import Column, Integer, String, JSON, DateTime
from sqlalchemy.sql import func
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'shared'))
from shared.database.db import Base


class Shipment(Base):
    __tablename__ = 'shipments'

    id = Column(Integer, primary_key=True)
    tracking_no = Column(String(100), unique=True, nullable=False)
    origin = Column(String(200))
    destination = Column(String(200))
    carrier = Column(String(100))
    status = Column(String(20), default='pending')
    current_location = Column(JSON, default={})
    eta = Column(DateTime)
    actual_arrival = Column(DateTime)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    def to_dict(self):
        return {
            'id': self.id, 'tracking_no': self.tracking_no,
            'origin': self.origin, 'destination': self.destination,
            'carrier': self.carrier, 'status': self.status,
            'current_location': self.current_location,
            'eta': self.eta.isoformat() if self.eta else None,
            'actual_arrival': self.actual_arrival.isoformat() if self.actual_arrival else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
