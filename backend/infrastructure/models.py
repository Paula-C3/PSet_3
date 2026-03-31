from sqlalchemy import Column, String, DateTime, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship
from datetime import datetime

from infrastructure.database import Base
from domain.enums import (
    Role,
    Severity,
    IncidentStatus,
    TaskStatus,
    NotificationStatus,
    NotificationChannel,
    EventType,
)


class UserModel(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(Enum(Role), nullable=False)

    created_incidents = relationship("IncidentModel", foreign_keys="[IncidentModel.created_by]")
    assigned_incidents = relationship("IncidentModel", foreign_keys="[IncidentModel.assigned_to]")
    tasks = relationship("TaskModel", back_populates="assignee")
    notifications = relationship("NotificationModel", back_populates="recipient_user")


class IncidentModel(Base):
    __tablename__ = "incidents"

    id = Column(String, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    severity = Column(Enum(Severity), nullable=False)
    status = Column(Enum(IncidentStatus), nullable=False)

    created_by = Column(String, ForeignKey("users.id"))
    assigned_to = Column(String, ForeignKey("users.id"), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    creator = relationship("UserModel", foreign_keys=[created_by])
    assignee = relationship("UserModel", foreign_keys=[assigned_to])
    tasks = relationship("TaskModel", back_populates="incident")


class TaskModel(Base):
    __tablename__ = "tasks"

    id = Column(String, primary_key=True, index=True)
    incident_id = Column(String, ForeignKey("incidents.id"))
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    status = Column(Enum(TaskStatus), nullable=False)

    assigned_to = Column(String, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

    incident = relationship("IncidentModel", back_populates="tasks")
    assignee = relationship("UserModel", back_populates="tasks")


class NotificationModel(Base):
    __tablename__ = "notifications"

    id = Column(String, primary_key=True, index=True)
    recipient = Column(String, ForeignKey("users.id"))
    channel = Column(Enum(NotificationChannel), nullable=False)
    message = Column(Text, nullable=False)
    event_type = Column(Enum(EventType), nullable=False)
    status = Column(Enum(NotificationStatus), nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)

    recipient_user = relationship("UserModel", back_populates="notifications")