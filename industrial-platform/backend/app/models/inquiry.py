from sqlalchemy import Column, Integer, String, Text, Numeric, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'shared'))
from shared.database.db import Base


class Inquiry(Base):
    __tablename__ = 'inquiries'

    id = Column(Integer, primary_key=True)
    buyer_id = Column(Integer, nullable=False)
    status = Column(String(20), default='pending')
    total_items = Column(Integer, default=0)
    remark = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    items = relationship('InquiryItem', back_populates='inquiry', lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'buyer_id': self.buyer_id,
            'status': self.status,
            'total_items': self.total_items,
            'remark': self.remark,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


class InquiryItem(Base):
    __tablename__ = 'inquiry_items'

    id = Column(Integer, primary_key=True)
    inquiry_id = Column(Integer, ForeignKey('inquiries.id'))
    product_sku_id = Column(Integer, ForeignKey('product_skus.id'))
    qty = Column(Integer, nullable=False)
    target_price = Column(Numeric(12, 2))
    remark = Column(Text)

    inquiry = relationship('Inquiry', back_populates='items')
    quotes = relationship('InquiryQuote', back_populates='item', lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'inquiry_id': self.inquiry_id,
            'product_sku_id': self.product_sku_id,
            'qty': self.qty,
            'target_price': float(self.target_price) if self.target_price else None,
            'remark': self.remark,
        }


class InquiryQuote(Base):
    __tablename__ = 'inquiry_quotes'

    id = Column(Integer, primary_key=True)
    inquiry_item_id = Column(Integer, ForeignKey('inquiry_items.id'))
    supplier_id = Column(Integer, ForeignKey('suppliers.id'))
    price = Column(Numeric(12, 2), nullable=False)
    delivery_days = Column(Integer)
    remark = Column(Text)
    status = Column(String(20), default='pending')
    created_at = Column(DateTime, server_default=func.now())

    item = relationship('InquiryItem', back_populates='quotes')

    def to_dict(self):
        return {
            'id': self.id,
            'inquiry_item_id': self.inquiry_item_id,
            'supplier_id': self.supplier_id,
            'price': float(self.price) if self.price else None,
            'delivery_days': self.delivery_days,
            'remark': self.remark,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
