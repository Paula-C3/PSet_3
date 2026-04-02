from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional, List
from datetime import datetime
from backend.domain.enums import Role, Severity, IncidentStatus, TaskStatus, NotificationStatus, NotificationChannel

# --- DTOs de Autenticacion ---
class UserCreateDTO(BaseModel):
    username: str
    password: str
    email: Optional[EmailStr] = None

class TokenDTO(BaseModel):
    access_token: str
    token_type: str = "bearer"

# --- DTOs de Usuario ---
class UserDTO(BaseModel):
    id: str
    username: str
    email: Optional[str] = None
    role: Role

    model_config = ConfigDict(from_attributes=True)

# --- DTOs de Incidentes ---
class IncidentCreateDTO(BaseModel):
    title: str = Field(..., min_length=5, max_length=100)
    description: str = Field(..., min_length=10)
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

# --- DTOs de Tareas ---
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

# --- DTOs de Notificaciones ---
class NotificationDTO(BaseModel):
    id: str
    recipient: str
    channel: NotificationChannel
    message: str
    status: NotificationStatus
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

# --- ALIAS DE COMPATIBILIDAD ---
# Estos permiten que los Use Cases viejos y las Rutas nuevas funcionen juntos
LoginRequest = UserCreateDTO
TokenResponse = TokenDTO
IncidentCreate = IncidentCreateDTO
TaskCreate = TaskCreateDTO