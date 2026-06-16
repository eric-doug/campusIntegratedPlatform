from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'shared'))
from shared.database.db import Base


class Enterprise(Base):
    __tablename__ = 'enterprises'

    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    unified_code = Column(String(50), unique=True, nullable=False)
    contact_person = Column(String(50))
    contact_phone = Column(String(20))
    address = Column(Text)
    industry = Column(String(100))
    status = Column(String(20), default='active')
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    def to_dict(self):
        return {
            'id': self.id, 'name': self.name, 'unified_code': self.unified_code,
            'contact_person': self.contact_person, 'contact_phone': self.contact_phone,
            'address': self.address, 'industry': self.industry, 'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
