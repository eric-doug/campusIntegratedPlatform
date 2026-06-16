from sqlalchemy import Column, Integer, String, Text, Numeric, JSON, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'shared'))
from shared.database.db import Base


class Order(Base):
    __tablename__ = 'orders'

    id = Column(Integer, primary_key=True)
    order_no = Column(String(50), unique=True, nullable=False)
    buyer_id = Column(Integer, nullable=False)
    status = Column(String(20), default='pending')
    total_amount = Column(Numeric(12, 2), nullable=False)
    payment_status = Column(String(20), default='unpaid')
    delivery_address = Column(JSON, default={})
    remark = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    items = relationship('OrderItem', back_populates='order', lazy='dynamic')
    payments = relationship('Payment', back_populates='order', lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'order_no': self.order_no,
            'buyer_id': self.buyer_id,
            'status': self.status,
            'total_amount': float(self.total_amount) if self.total_amount else None,
            'payment_status': self.payment_status,
            'delivery_address': self.delivery_address,
            'remark': self.remark,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


class OrderItem(Base):
    __tablename__ = 'order_items'

    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey('orders.id'))
    product_sku_id = Column(Integer, ForeignKey('product_skus.id'))
    qty = Column(Integer, nullable=False)
    unit_price = Column(Numeric(12, 2), nullable=False)
    amount = Column(Numeric(12, 2), nullable=False)

    order = relationship('Order', back_populates='items')

    def to_dict(self):
        return {
            'id': self.id,
            'order_id': self.order_id,
            'product_sku_id': self.product_sku_id,
            'qty': self.qty,
            'unit_price': float(self.unit_price) if self.unit_price else None,
            'amount': float(self.amount) if self.amount else None,
        }
