from sqlalchemy import Column, Integer, String, JSON, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'shared'))
from shared.database.db import Base


class ReportTemplate(Base):
    __tablename__ = 'report_templates'

    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    department = Column(String(100), nullable=False)
    format_config = Column(JSON, default={})
    period_type = Column(String(30), nullable=False)
    status = Column(String(20), default='active')
    created_at = Column(DateTime, server_default=func.now())

    forms = relationship('ReportForm', back_populates='template', lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id, 'name': self.name, 'department': self.department,
            'format_config': self.format_config, 'period_type': self.period_type,
            'status': self.status, 'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class ReportForm(Base):
    __tablename__ = 'report_forms'

    id = Column(Integer, primary_key=True)
    enterprise_id = Column(Integer, nullable=False)
    template_id = Column(Integer, nullable=False)
    period = Column(String(50), nullable=False)
    data = Column(JSON, default={})
    status = Column(String(20), default='draft')
    submitted_at = Column(DateTime)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    template = relationship('ReportTemplate', back_populates='forms')

    def to_dict(self):
        return {
            'id': self.id, 'enterprise_id': self.enterprise_id, 'template_id': self.template_id,
            'period': self.period, 'data': self.data, 'status': self.status,
            'submitted_at': self.submitted_at.isoformat() if self.submitted_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
