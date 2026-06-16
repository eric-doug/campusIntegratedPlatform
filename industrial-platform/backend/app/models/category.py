from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'shared'))
from shared.database.db import Base


class Category(Base):
    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    parent_id = Column(Integer, ForeignKey('categories.id'))
    level = Column(Integer, default=1)
    sort_order = Column(Integer, default=0)
    icon = Column(String(255))
    status = Column(String(20), default='active')

    children = relationship('Category', backref='parent', remote_side=[id], lazy='dynamic')
    products = relationship('Product', back_populates='category')

    def to_dict(self, include_children=False):
        data = {
            'id': self.id,
            'name': self.name,
            'parent_id': self.parent_id,
            'level': self.level,
            'sort_order': self.sort_order,
            'icon': self.icon,
            'status': self.status,
        }
        if include_children:
            data['children'] = [c.to_dict() for c in self.children]
        return data
