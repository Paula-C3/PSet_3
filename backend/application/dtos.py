from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from backend.domain.enums import Role, Severity, IncidentStatus, TaskStatus, NotificationStatus, NotificationChannel

# --- DTOs de Autenticación ---
class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: Role

# --- DTOs de Usuario ---
class UserDTO(BaseModel):
    id: str
    name: str
    email: str
    role: Role

    class Config:
        from_attributes = True

# --- DTOs de Incidentes ---
class IncidentCreate(BaseModel):
    title: str = Field(..., min_length=5, max_length=100)
    description: str = Field(..., min_length=10)
    severity: Severity

class IncidentUpdate(BaseModel):
    status: Optional[IncidentStatus] = None
    assigned_to: Optional[str] = None

class IncidentDTO(BaseModel):
    id: str
    title: str
    description: str
    severity: Severity
    status: IncidentStatus
    created_by: str
    assigned_to: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

# --- DTOs de Tareas ---
class TaskCreate(BaseModel):
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

    class Config:
        from_attributes = True

# --- DTOs de Notificaciones ---
class NotificationDTO(BaseModel):
    id: str
    recipient: str
    channel: NotificationChannel
    message: str
    status: NotificationStatus
    created_at: datetime

    class Config:
        from_attributes = True