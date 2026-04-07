from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional, List
from datetime import datetime
from backend.domain.enums import Role, Severity, IncidentStatus, TaskStatus, NotificationStatus, NotificationChannel


# DTOs de Autenticacion 

class UserCreateDTO(BaseModel):
    """Usado para registro. name es opcional para compatibilidad."""
    name: Optional[str] = None
    email: EmailStr
    password: str
    role: Optional[Role] = Role.OPERATOR


class LoginDTO(BaseModel):
    """Usado exclusivamente para login."""
    email: EmailStr
    password: str


class TokenDTO(BaseModel):
    access_token: str
    token_type: str = "bearer"


# DTOs de Usuario 

class UserDTO(BaseModel):
    id: str
    name: Optional[str] = None
    email: Optional[str] = None
    role: Role

    model_config = ConfigDict(from_attributes=True)


# DTOs de Incidentes 

class IncidentCreateDTO(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., min_length=1)
    severity: Severity


class IncidentDTO(BaseModel):
    id: str
    title: str
    description: str
    severity: Severity
    status: IncidentStatus
    created_by: str
    assigned_to: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# DTOs de Tareas 

class TaskCreateDTO(BaseModel):
    incident_id: str
    title: str
    description: str
    assigned_to: str


class TaskDTO(BaseModel):
    id: str
    incident_id: str
    title: str
    description: str
    status: TaskStatus
    assigned_to: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# DTOs de Notificaciones

class NotificationDTO(BaseModel):
    id: str
    recipient: str
    channel: NotificationChannel
    message: str
    event_type: Optional[str] = None
    status: NotificationStatus
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ALIAS DE COMPATIBILIDAD 
LoginRequest = LoginDTO
TokenResponse = TokenDTO
IncidentCreate = IncidentCreateDTO
TaskCreate = TaskCreateDTO