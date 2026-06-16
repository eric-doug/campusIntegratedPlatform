from sqlalchemy import Column, Integer, String, Numeric, JSON, DateTime
from sqlalchemy.sql import func
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'shared'))
from shared.database.db import Base


class VesselDynamic(Base):
    __tablename__ = 'vessel_dynamics'

    id = Column(Integer, primary_key=True)
    vessel_name = Column(String(100), nullable=False)
    imo = Column(String(20))
    port = Column(String(100))
    eta = Column(DateTime)
    ata = Column(DateTime)
    berth_status = Column(String(30))
    cargo_progress = Column(Numeric(5, 2), default=0)
    raw_data = Column(JSON, default={})
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    def to_dict(self):
        return {
            'id': self.id, 'vessel_name': self.vessel_name, 'imo': self.imo,
            'port': self.port, 'eta': self.eta.isoformat() if self.eta else None,
            'ata': self.ata.isoformat() if self.ata else None,
            'berth_status': self.berth_status,
            'cargo_progress': float(self.cargo_progress) if self.cargo_progress else None,
            'raw_data': self.raw_data,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
