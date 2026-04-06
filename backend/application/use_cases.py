from typing import List, Optional
from fastapi import Depends           #type:ignore

from backend.domain.entities import User, Incident, Task

from backend.domain.repositories import UserRepository, IncidentRepository, TaskRepository
from backend.domain.factory import IncidentFactory
from backend.domain.enums import EventType, Role

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

    def register_user(self, data: UserCreateDTO) -> User:
        from backend.domain.entities import User
        from backend.domain.enums import Role
        from backend.infrastructure.auth import hash_password
        import uuid

        hashed_password = hash_password(data.password)

        user = User(
            id=str(uuid.uuid4()),
            name=data.username,
            email=data.email if data.email else data.username,
            password=hashed_password,
            role=Role.OPERATOR
        )

        return self.user_repo.save(user)

    def login(self, data: UserCreateDTO) -> TokenDTO:
        from backend.infrastructure.auth import verify_password, create_access_token

        # usamos username como email
        email = data.email if data.email else data.username

        user = self.user_repo.find_by_email(email)

        if not user:
            raise ValueError("Usuario no encontrado")

        if not verify_password(data.password, user.password):
            raise ValueError("Credenciales inválidas")

        token = create_access_token(
            user_id=user.id,
            role=str(user.role)
        )

        return TokenDTO(access_token=token)

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

    def get_all_incidents(self, user: User) -> List[Incident]:
        if user.role == Role.ADMIN or user.role == Role.SUPERVISOR:
            return self.incident_repo.find_all()
        return self.incident_repo.find_by_creator(user.id)

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
        # Método de borrado no implementado en repositorio
        raise NotImplementedError("delete no está implementado en IncidentRepository")

    def get_incident_detail(self, incident_id: str) -> Incident:
        incident = self.incident_repo.find_by_id(incident_id)
        if not incident:
            raise ValueError("Incidente no encontrado")
        return incident
    
    def resolve_incident(self, incident_id: str) -> Incident:
        incident = self.incident_repo.find_by_id(incident_id)
        if not incident:
            raise ValueError("Incidente no encontrado")
        incident.resolve()
        updated = self.incident_repo.save(incident)
        self.event_bus.publish(
            EventType.INCIDENT_STATUS_CHANGED,
            {"id": updated.id, "status": str(updated.status)}
        )
        return updated
    
    def change_status(self, incident_id: str, new_status: str) -> Incident:
        incident = self.incident_repo.find_by_id(incident_id)
        if not incident:
            raise ValueError("Incidente no encontrado")

        status_upper = new_status.upper()

        if status_upper == "ASSIGNED":
            # usa el creador como assignee por defecto si no tiene uno asignado
            assignee = incident.assigned_to or incident.created_by
            incident.assign(assignee)
        elif status_upper == "IN_PROGRESS":
            incident.start_progress()
        elif status_upper == "RESOLVED":
            incident.resolve()
        elif status_upper == "CLOSED":
            incident.close()
        else:
            raise ValueError(f"Estado inválido: {new_status}")

        updated = self.incident_repo.save(incident)
        self.event_bus.publish(
            EventType.INCIDENT_STATUS_CHANGED,
            {"id": updated.id, "status": str(updated.status)}
        )
        return updated
    
class TaskUseCases:

    def __init__(
        self,
        task_repo: TaskRepository = Depends(SQLAlchemyTaskRepository),
        event_bus: EventBus = Depends()
    ):
        self.task_repo = task_repo
        self.event_bus = event_bus

    def create_task(self, data: TaskCreateDTO) -> Task:
        task = Task(
            incident_id=data.incident_id,
            title=data.title,
            description=data.description,
            assigned_to=data.assigned_to
        )
        saved = self.task_repo.save(task)
        self.event_bus.publish(
            EventType.TASK_CREATED,
            {"id": saved.id, "incident_id": saved.incident_id}
        )
        return saved
    
    def get_tasks(self, user: User) -> List[Task]:
        if user.role == Role.ADMIN or user.role == Role.SUPERVISOR:
            return self.task_repo.find_all()
        return self.task_repo.find_by_assignee(user.id)
    
    def change_status(self, task_id: str, new_status) -> Task:
        task = self.task_repo.find_by_id(task_id)
        if not task:
            raise ValueError("Tarea no encontrada")
        task.status = new_status
        updated = self.task_repo.save(task)
        self.event_bus.publish(
            EventType.TASK_DONE,
            {"id": updated.id}
        )
        return updated
    
class NotificationUseCases:

    def __init__(self, notification_repo):
        self.notification_repo = notification_repo

    def get_notifications(self, user: User):
        if user.role == Role.ADMIN:
            return self.notification_repo.find_all()
        return self.notification_repo.find_by_recipient(user.id)