from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'shared'))
from shared.database.db import Base


class InboundOrder(Base):
    __tablename__ = 'inbound_orders'

    id = Column(Integer, primary_key=True)
    order_no = Column(String(50), unique=True, nullable=False)
    warehouse_id = Column(Integer, nullable=False)
    supplier_id = Column(Integer)
    status = Column(String(20), default='pending')
    total_qty = Column(Integer, default=0)
    remark = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    items = relationship('InboundItem', back_populates='order', lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id, 'order_no': self.order_no, 'warehouse_id': self.warehouse_id,
            'supplier_id': self.supplier_id, 'status': self.status, 'total_qty': self.total_qty,
            'remark': self.remark, 'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class InboundItem(Base):
    __tablename__ = 'inbound_items'

    id = Column(Integer, primary_key=True)
    inbound_order_id = Column(Integer, nullable=False)
    product_sku_id = Column(Integer)
    qty = Column(Integer, nullable=False)
    batch_no = Column(String(50))
    location_id = Column(Integer)
    status = Column(String(20), default='pending')

    order = relationship('InboundOrder', back_populates='items')

    def to_dict(self):
        return {
            'id': self.id, 'inbound_order_id': self.inbound_order_id,
            'product_sku_id': self.product_sku_id, 'qty': self.qty,
            'batch_no': self.batch_no, 'location_id': self.location_id, 'status': self.status,
        }
