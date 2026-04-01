from typing import List, Optional
from backend.domain.entities import User, Incident, Task
from backend.domain.repositories import UserRepository, IncidentRepository, TaskRepository, NotificationRepository
from backend.domain.factory import IncidentFactory
from backend.domain.observer import EventBus
from backend.domain.enums import EventType, Role
from backend.infrastructure.auth import verify_password, create_access_token
from backend.application.dtos import LoginRequest, TokenResponse, IncidentCreate, TaskCreate

class AuthUseCases:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    def login(self, data: LoginRequest) -> TokenResponse:
        user = self.user_repo.find_by_email(data.email)
        if not user or not verify_password(data.password, user.hashed_password):
            raise ValueError("Credenciales invalidas")
        
        token = create_access_token(user_id=user.id, role=user.role.value)
        return TokenResponse(access_token=token, role=user.role)

class IncidentUseCases:
    def __init__(
        self, 
        incident_repo: IncidentRepository, 
        user_repo: UserRepository,
        event_bus: EventBus
    ):
        self.incident_repo = incident_repo
        self.user_repo = user_repo
        self.event_bus = event_bus

    def create_incident(self, data: IncidentCreate, creator_id: str) -> Incident:
        incident = IncidentFactory.create(
            title=data.title,
            description=data.description,
            severity=data.severity.value,
            created_by=creator_id
        )
        saved_incident = self.incident_repo.save(incident)
        
        # Notificar evento
        self.event_bus.publish(
            EventType.INCIDENT_CREATED, 
            {"id": saved_incident.id, "title": saved_incident.title}
        )
        return saved_incident

    def assign_incident(self, incident_id: str, assignee_id: str) -> Incident:
        incident = self.incident_repo.find_by_id(incident_id)
        if not incident:
            raise ValueError("Incidente no encontrado")
        
        incident.assign(assignee_id)
        updated = self.incident_repo.save(incident)
        
        self.event_bus.publish(
            EventType.INCIDENT_ASSIGNED, 
            {"id": updated.id, "assigned_to": assignee_id}
        )
        return updated

class TaskUseCases:
    def __init__(self, task_repo: TaskRepository, event_bus: EventBus):
        self.task_repo = task_repo
        self.event_bus = event_bus

    def create_task(self, data: TaskCreate) -> Task:
        task = Task(
            incident_id=data.incident_id,
            title=data.title,
            description=data.description,
            assigned_to=data.assigned_to
        )
        saved_task = self.task_repo.save(task)
        
        self.event_bus.publish(
            EventType.TASK_CREATED, 
            {"id": saved_task.id, "incident_id": saved_task.incident_id}
        )
        return saved_task