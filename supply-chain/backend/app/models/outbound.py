from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'shared'))
from shared.database.db import Base


class OutboundOrder(Base):
    __tablename__ = 'outbound_orders'

    id = Column(Integer, primary_key=True)
    order_no = Column(String(50), unique=True, nullable=False)
    warehouse_id = Column(Integer, nullable=False)
    type = Column(String(30), nullable=False)
    status = Column(String(20), default='pending')
    total_qty = Column(Integer, default=0)
    remark = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    items = relationship('OutboundItem', back_populates='order', lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id, 'order_no': self.order_no, 'warehouse_id': self.warehouse_id,
            'type': self.type, 'status': self.status, 'total_qty': self.total_qty,
            'remark': self.remark, 'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class OutboundItem(Base):
    __tablename__ = 'outbound_items'

    id = Column(Integer, primary_key=True)
    outbound_order_id = Column(Integer, nullable=False)
    product_sku_id = Column(Integer)
    qty = Column(Integer, nullable=False)
    batch_no = Column(String(50))
    location_id = Column(Integer)

    order = relationship('OutboundOrder', back_populates='items')

    def to_dict(self):
        return {
            'id': self.id, 'outbound_order_id': self.outbound_order_id,
            'product_sku_id': self.product_sku_id, 'qty': self.qty,
            'batch_no': self.batch_no, 'location_id': self.location_id,
        }
