from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'shared'))
from shared.database.db import Base


class Payment(Base):
    __tablename__ = 'payments'

    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey('orders.id'))
    payment_no = Column(String(100), unique=True)
    channel = Column(String(30), nullable=False)
    amount = Column(Numeric(12, 2), nullable=False)
    status = Column(String(20), default='pending')
    paid_at = Column(DateTime)
    created_at = Column(DateTime, server_default=func.now())

    order = relationship('Order', back_populates='payments')

    def to_dict(self):
        return {
            'id': self.id,
            'order_id': self.order_id,
            'payment_no': self.payment_no,
            'channel': self.channel,
            'amount': float(self.amount) if self.amount else None,
            'status': self.status,
            'paid_at': self.paid_at.isoformat() if self.paid_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
