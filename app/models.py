from datetime import date as date_type, datetime
from enum import Enum

from sqlalchemy import Boolean, Column, Date, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database import Base


class TaskStatus(str, Enum):
    pendiente = "pendiente"
    completada = "completada"


class TaskPriority(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


def utc_now() -> datetime:
    return datetime.utcnow()


class UserModel(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(120), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, nullable=False, default=utc_now)

    tasks = relationship("TaskModel", back_populates="owner", cascade="all, delete-orphan")
    refresh_tokens = relationship("RefreshTokenModel", back_populates="user", cascade="all, delete-orphan")


class TaskModel(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(120), nullable=False, index=True)
    description = Column(String(500), nullable=True)
    status = Column(String(20), nullable=False, default=TaskStatus.pendiente.value, index=True)
    priority = Column(String(20), nullable=False, default=TaskPriority.medium.value, index=True)
    date = Column(Date, nullable=False, default=date_type.today, index=True)
    due_date = Column(Date, nullable=True, index=True)
    completed_at = Column(DateTime, nullable=True)
    deleted_at = Column(DateTime, nullable=True, index=True)
    created_at = Column(DateTime, nullable=False, default=utc_now)
    updated_at = Column(DateTime, nullable=False, default=utc_now, onupdate=utc_now)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    owner = relationship("UserModel", back_populates="tasks")
    audit_logs = relationship("TaskAuditLogModel", back_populates="task", cascade="all, delete-orphan")


class RefreshTokenModel(Base):
    __tablename__ = "refresh_tokens"

    id = Column(Integer, primary_key=True, index=True)
    token_hash = Column(String(255), unique=True, nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    expires_at = Column(DateTime, nullable=False)
    revoked = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, nullable=False, default=utc_now)

    user = relationship("UserModel", back_populates="refresh_tokens")


class TaskAuditLogModel(Base):
    __tablename__ = "task_audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    action = Column(String(60), nullable=False)
    field_name = Column(String(80), nullable=True)
    old_value = Column(Text, nullable=True)
    new_value = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, default=utc_now)

    task = relationship("TaskModel", back_populates="audit_logs")
