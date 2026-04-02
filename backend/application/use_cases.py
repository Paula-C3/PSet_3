from typing import List, Optional
from fastapi import Depends

from backend.domain.entities import User, Incident, Task
# Aquí quitamos EventBus porque no es un repositorio
from backend.domain.repositories import UserRepository, IncidentRepository, TaskRepository
from backend.domain.factory import IncidentFactory
from backend.domain.enums import EventType, Role
# Aquí traemos el EventBus de donde realmente vive
from backend.domain.observer import EventBus
from backend.infrastructure.auth import verify_password, create_access_token
from backend.application.dtos import UserCreateDTO, TokenDTO, IncidentCreateDTO, TaskCreateDTO

# Importamos las implementaciones reales para la inyección por defecto
from backend.infrastructure.repositories import (
    SQLAlchemyUserRepository, 
    SQLAlchemyIncidentRepository, 
    SQLAlchemyTaskRepository
)
from backend.domain.observer import EventBus as DomainEventBus

class AuthUseCases:
    def __init__(self, user_repo: UserRepository = Depends(SQLAlchemyUserRepository)):
        self.user_repo = user_repo

class IncidentUseCases:
    def __init__(
        self, 
        incident_repo: IncidentRepository = Depends(SQLAlchemyIncidentRepository), 
        user_repo: UserRepository = Depends(SQLAlchemyUserRepository),
        event_bus: EventBus = Depends() # FastAPI buscara la instancia de EventBus
    ):
        self.incident_repo = incident_repo
        self.user_repo = user_repo
        self.event_bus = event_bus

    def create_incident(self, data: IncidentCreateDTO, creator_id: str) -> Incident:
        incident = IncidentFactory.create(
            title=data.title,
            description=data.description,
            severity=data.severity,
            created_by=creator_id
        )
        saved_incident = self.incident_repo.save(incident)
        
        self.event_bus.publish(
            EventType.INCIDENT_CREATED, 
            {"id": saved_incident.id, "title": saved_incident.title}
        )
        return saved_incident

    def get_all_incidents(self) -> List[Incident]:
        return self.incident_repo.find_all()

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

    def delete_incident(self, incident_id: str):
        self.incident_repo.delete(incident_id)