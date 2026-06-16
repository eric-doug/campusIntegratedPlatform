from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'shared'))
from shared.database.db import Base


class Supplier(Base):
    __tablename__ = 'suppliers'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    code = Column(String(50), unique=True, nullable=False)
    contact_person = Column(String(50))
    contact_phone = Column(String(20))
    business_license = Column(String(100))
    address = Column(Text)
    status = Column(String(20), default='active')
    audit_status = Column(String(20), default='pending')
    audit_remark = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    products = relationship('Product', back_populates='supplier')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'code': self.code,
            'contact_person': self.contact_person,
            'contact_phone': self.contact_phone,
            'business_license': self.business_license,
            'address': self.address,
            'status': self.status,
            'audit_status': self.audit_status,
            'audit_remark': self.audit_remark,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
