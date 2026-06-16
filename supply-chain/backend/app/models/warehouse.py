from sqlalchemy import Column, Integer, String, Numeric, JSON, DateTime, UniqueConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'shared'))
from shared.database.db import Base


class Warehouse(Base):
    __tablename__ = 'warehouses'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    code = Column(String(50), unique=True, nullable=False)
    location = Column(JSON, default={})
    capacity = Column(Numeric(12, 2))
    used_capacity = Column(Numeric(12, 2), default=0)
    status = Column(String(20), default='active')
    created_at = Column(DateTime, server_default=func.now())

    locations = relationship('WarehouseLocation', back_populates='warehouse', lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id, 'name': self.name, 'code': self.code,
            'location': self.location, 'capacity': float(self.capacity) if self.capacity else None,
            'used_capacity': float(self.used_capacity) if self.used_capacity else None,
            'status': self.status, 'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class WarehouseLocation(Base):
    __tablename__ = 'warehouse_locations'
    __table_args__ = (UniqueConstraint('warehouse_id', 'zone', 'shelf', 'bin'),)

    id = Column(Integer, primary_key=True)
    warehouse_id = Column(Integer, Warehouse.__table__.c.id.type, nullable=False)
    zone = Column(String(30))
    shelf = Column(String(30))
    bin = Column(String(30))
    status = Column(String(20), default='active')

    warehouse = relationship('Warehouse', back_populates='locations')

    def to_dict(self):
        return {
            'id': self.id, 'warehouse_id': self.warehouse_id,
            'zone': self.zone, 'shelf': self.shelf, 'bin': self.bin, 'status': self.status,
        }
