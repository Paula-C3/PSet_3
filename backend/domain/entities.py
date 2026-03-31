from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

from backend.domain.enums import (
    EventType,
    IncidentStatus,
    NotificationChannel,
    NotificationStatus,
    Role,
    Severity,
    TaskStatus,
)
from backend.domain.state import IncidentState, state_for


def _new_id() -> str:
    return str(uuid.uuid4())


def _now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass
class User:
    name: str
    email: str
    hashed_password: str
    role: Role
    id: str = field(default_factory=_new_id)

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("El nombre de usuario no puede estar vacío.")
        if "@" not in self.email:
            raise ValueError(f"Correo electrónico no válido: {self.email}")


@dataclass
class Incident:
    title: str
    description: str
    severity: Severity
    created_by: str
    id: str = field(default_factory=_new_id)
    status: IncidentStatus = IncidentStatus.OPEN
    assigned_to: Optional[str] = None
    created_at: datetime = field(default_factory=_now)
    _state: IncidentState = field(init=False, repr=False, compare=False)

    def __post_init__(self) -> None:
        if not self.title.strip():
            raise ValueError("El título del incidente no puede estar vacío.")
        if not self.description.strip():
            raise ValueError("La descripción del incidente no puede estar vacía.")
        self._state = state_for(self.status)

    def assign(self, assignee_id: str) -> None:
        self._state.assign(self, assignee_id)

    def start_progress(self) -> None:
        self._state.start_progress(self)

    def resolve(self) -> None:
        self._state.resolve(self)

    def close(self) -> None:
        self._state.close(self)


@dataclass
class Task:
    incident_id: str
    title: str
    description: str
    assigned_to: str
    id: str = field(default_factory=_new_id)
    status: TaskStatus = TaskStatus.OPEN
    created_at: datetime = field(default_factory=_now)

    def __post_init__(self) -> None:
        if not self.title.strip():
            raise ValueError("El título de la tarea no puede estar vacío.")
        if not self.description.strip():
            raise ValueError("La descripción de la tarea no puede estar vacía.")


@dataclass
class Notification:
    recipient: str
    channel: NotificationChannel
    message: str
    event_type: EventType
    id: str = field(default_factory=_new_id)
    status: NotificationStatus = NotificationStatus.PENDING
    created_at: datetime = field(default_factory=_now)

    def mark_sent(self) -> None:
        self.status = NotificationStatus.SENT

    def mark_failed(self) -> None:
        self.status = NotificationStatus.FAILED