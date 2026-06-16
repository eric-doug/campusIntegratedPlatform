from sqlalchemy import Column, Integer, String, DateTime, UniqueConstraint
from sqlalchemy.sql import func
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'shared'))
from shared.database.db import Base


class Inventory(Base):
    __tablename__ = 'inventory'
    __table_args__ = (UniqueConstraint('warehouse_id', 'product_sku_id', 'batch_no'),)

    id = Column(Integer, primary_key=True)
    warehouse_id = Column(Integer, nullable=False)
    product_sku_id = Column(Integer, nullable=False)
    qty = Column(Integer, default=0)
    locked_qty = Column(Integer, default=0)
    batch_no = Column(String(50))
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    def to_dict(self):
        return {
            'id': self.id, 'warehouse_id': self.warehouse_id,
            'product_sku_id': self.product_sku_id, 'qty': self.qty,
            'locked_qty': self.locked_qty, 'batch_no': self.batch_no,
            'available_qty': self.qty - self.locked_qty,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
