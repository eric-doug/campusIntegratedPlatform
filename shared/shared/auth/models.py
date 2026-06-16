from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, UniqueConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..database.db import Base


class User(Base):
    __tablename__ = 'users'
    __table_args__ = {'schema': 'shared_auth'}

    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    phone = Column(String(20), unique=True)
    email = Column(String(100), unique=True)
    password_hash = Column(String(255), nullable=False)
    status = Column(String(20), default='active')
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    roles = relationship('Role', secondary='shared_auth.user_roles', back_populates='users')


class Role(Base):
    __tablename__ = 'roles'
    __table_args__ = {'schema': 'shared_auth'}

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    code = Column(String(50), unique=True, nullable=False)
    description = Column(Text)

    users = relationship('User', secondary='shared_auth.user_roles', back_populates='roles')


class UserRole(Base):
    __tablename__ = 'user_roles'
    __table_args__ = (
        UniqueConstraint('user_id', 'role_id'),
        {'schema': 'shared_auth'},
    )

    user_id = Column(Integer, ForeignKey('shared_auth.users.id'), primary_key=True)
    role_id = Column(Integer, ForeignKey('shared_auth.roles.id'), primary_key=True)


class PlatformPermission(Base):
    __tablename__ = 'platform_permissions'
    __table_args__ = (
        UniqueConstraint('platform', 'resource', 'action', 'role_id'),
        {'schema': 'shared_auth'},
    )

    id = Column(Integer, primary_key=True)
    platform = Column(String(30), nullable=False)
    resource = Column(String(50), nullable=False)
    action = Column(String(30), nullable=False)
    role_id = Column(Integer, ForeignKey('shared_auth.roles.id'))
