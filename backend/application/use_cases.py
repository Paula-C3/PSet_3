from typing import List, Optional
from fastapi import Depends  # type:ignore

from backend.domain.entities import User, Incident, Task

from backend.domain.repositories import UserRepository, IncidentRepository, TaskRepository
from backend.domain.factory import IncidentFactory
from backend.domain.enums import EventType, Role

from backend.domain.observer import EventBus
from backend.infrastructure.auth import verify_password, create_access_token
from backend.application.dtos import UserCreateDTO, LoginDTO, TokenDTO, IncidentCreateDTO, TaskCreateDTO

from backend.infrastructure.repositories import (
    SQLAlchemyUserRepository,
    SQLAlchemyIncidentRepository,
    SQLAlchemyTaskRepository
)

#Gestiona el registro de usuarios, login, creación y gestión de incidentes y tareas, y notificaciones. Cada método implementa la lógica de negocio correspondiente, interactuando con los repositorios para acceder a los datos y publicando eventos en el bus cuando es necesario.
class AuthUseCases:
    def __init__(self, user_repo: UserRepository = Depends(SQLAlchemyUserRepository)):
        self.user_repo = user_repo
#crea un nuevo usuario, hashea su contraseña y lo guarda en la base de datos. Si no se especifica un nombre, se usa el email como nombre. Si no se especifica un rol, se asigna el rol de OPERATOR por defecto.
    def register_user(self, data: UserCreateDTO) -> User:
        from backend.domain.entities import User
        from backend.domain.enums import Role
        from backend.infrastructure.auth import hash_password
        import uuid

        hashed_password = hash_password(data.password)

        user = User(
            id=str(uuid.uuid4()),
            name=data.name or data.email,
            email=data.email,
            password=hashed_password,
            role=data.role or Role.OPERATOR
        )

        return self.user_repo.save(user)
#verifica las credenciales del usuario, y si son válidas, genera un token JWT con el ID y el rol del usuario. Si el usuario no existe o las credenciales son inválidas, lanza un error.
    def login(self, data: LoginDTO) -> TokenDTO:
        from backend.infrastructure.auth import verify_password, create_access_token

        user = self.user_repo.find_by_email(data.email)

        if not user:
            raise ValueError("Usuario no encontrado")

        if not verify_password(data.password, user.password):
            raise ValueError("Credenciales invalidas")

        token = create_access_token(
            user_id=user.id,
            role= user.role.value if hasattr(user.role, 'value') else str(user.role)
        )

        return TokenDTO(access_token=token)

#Gestiona la lógica relacionada con incidentes.
class IncidentUseCases:
    def __init__(
        self,
        incident_repo: IncidentRepository = Depends(SQLAlchemyIncidentRepository),
        user_repo: UserRepository = Depends(SQLAlchemyUserRepository),
        event_bus: EventBus = Depends()
    ):
        self.incident_repo = incident_repo
        self.user_repo = user_repo
        self.event_bus = event_bus
#Crea un incidente y publica un evento.
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
            {
                "id": saved_incident.id,
                "title": saved_incident.title,
                "created_by": saved_incident.created_by,
                "assigned_to": saved_incident.assigned_to
            }
        )
        return saved_incident
#Devuelve la lista de incidentes que el usuario tiene permiso para ver. 
    def get_all_incidents(self, user: User) -> List[Incident]:
        if user.role == Role.ADMIN or user.role == Role.SUPERVISOR:
            return self.incident_repo.find_all()
        # OPERATOR: ve incidentes creados por él O asignados a él
        created = self.incident_repo.find_by_creator(user.id)
        assigned = self.incident_repo.find_by_assignee(user.id)
        seen_ids = set()
        result = []
        for incident in created + assigned:
            if incident.id not in seen_ids:
                seen_ids.add(incident.id)
                result.append(incident)
        return result
#Asigna un incidente a un usuario y publica un evento
    def assign_incident(self, incident_id: str, assignee_id: str) -> Incident:
        incident = self.incident_repo.find_by_id(incident_id)
        if not incident:
            raise ValueError("Incidente no encontrado")

        incident.assign(assignee_id)
        updated = self.incident_repo.save(incident)

        self.event_bus.publish(
            EventType.INCIDENT_ASSIGNED,
            {
                "id": updated.id,
                "assigned_to": assignee_id,
                "created_by": updated.created_by
            }
        )
        return updated

    def delete_incident(self, incident_id: str):
        raise NotImplementedError("delete no esta implementado en IncidentRepository")

#def delete_incident(self, incident_id: str):
 #   incident = self.incident_repo.find_by_id(incident_id)
  #  if not incident:
   #     raise ValueError("Incidente no encontrado")
    #self.incident_repo.delete(incident_id)
    #self.event_bus.publish(
     #   EventType.INCIDENT_DELETED,
      #  {
       #     "id": incident_id,
        #    "deleted_by": incident.created_by
        #}
    #)
    #Busca un incidente por su ID.
    def get_incident_detail(self, incident_id: str) -> Incident:
        incident = self.incident_repo.find_by_id(incident_id)
        if not incident:
            raise ValueError("Incidente no encontrado")
        return incident
#Marca un incidente como resuelto
    def resolve_incident(self, incident_id: str) -> Incident:
        incident = self.incident_repo.find_by_id(incident_id)
        if not incident:
            raise ValueError("Incidente no encontrado")
        incident.resolve()
        updated = self.incident_repo.save(incident)
        self.event_bus.publish(
            EventType.INCIDENT_STATUS_CHANGED,
            {
                "id": updated.id,
                "status": str(updated.status),
                "created_by": updated.created_by,
                "assigned_to": updated.assigned_to
            }
        )
        return updated

    def change_status(self, incident_id: str, new_status: str) -> Incident:
        incident = self.incident_repo.find_by_id(incident_id)
        if not incident:
            raise ValueError("Incidente no encontrado")

        status_upper = new_status.upper()

        if status_upper == "ASSIGNED":
            assignee = incident.assigned_to or incident.created_by
            incident.assign(assignee)
        elif status_upper == "IN_PROGRESS":
            incident.start_progress()
        elif status_upper == "RESOLVED":
            incident.resolve()
        elif status_upper == "CLOSED":
            incident.close()
        else:
            raise ValueError(f"Estado invalido: {new_status}")

        updated = self.incident_repo.save(incident)
        self.event_bus.publish(
            EventType.INCIDENT_STATUS_CHANGED,
            {
                "id": updated.id,
                "status": str(updated.status),
                "created_by": updated.created_by,
                "assigned_to": updated.assigned_to
            }
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
            {
                "id": saved.id,
                "incident_id": saved.incident_id,
                "assigned_to": saved.assigned_to
            }
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
            {
                "id": updated.id,
                "assigned_to": updated.assigned_to
            }
        )
        return updated


class NotificationUseCases:

    def __init__(self, notification_repo):
        self.notification_repo = notification_repo

    def get_notifications(self, user: User):
        if user.role == Role.ADMIN:
            return self.notification_repo.find_all()
        return self.notification_repo.find_by_recipient(user.id)