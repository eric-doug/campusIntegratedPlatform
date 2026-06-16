from sqlalchemy import Column, Integer, String, Text, Numeric, JSON, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'shared'))
from shared.database.db import Base


class Product(Base):
    __tablename__ = 'products'

    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    category_id = Column(Integer, ForeignKey('categories.id'))
    supplier_id = Column(Integer, ForeignKey('suppliers.id'))
    specs = Column(JSON, default={})
    unit = Column(String(20))
    description = Column(Text)
    images = Column(JSON, default=[])
    status = Column(String(20), default='active')
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    skus = relationship('ProductSku', back_populates='product', lazy='dynamic')
    category = relationship('Category', back_populates='products')
    supplier = relationship('Supplier', back_populates='products')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'category_id': self.category_id,
            'supplier_id': self.supplier_id,
            'specs': self.specs,
            'unit': self.unit,
            'description': self.description,
            'images': self.images,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


class ProductSku(Base):
    __tablename__ = 'product_skus'

    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey('products.id'))
    sku_code = Column(String(100), unique=True, nullable=False)
    attributes = Column(JSON, default={})
    price = Column(Numeric(12, 2), nullable=False)
    original_price = Column(Numeric(12, 2))
    stock = Column(Integer, default=0)
    min_order_qty = Column(Integer, default=1)
    status = Column(String(20), default='active')

    product = relationship('Product', back_populates='skus')

    def to_dict(self):
        return {
            'id': self.id,
            'product_id': self.product_id,
            'sku_code': self.sku_code,
            'attributes': self.attributes,
            'price': float(self.price) if self.price else None,
            'original_price': float(self.original_price) if self.original_price else None,
            'stock': self.stock,
            'min_order_qty': self.min_order_qty,
            'status': self.status,
        }
