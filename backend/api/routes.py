from backend.domain.entities import User
from fastapi import APIRouter, Depends, HTTPException, status  # type:ignore
from typing import List
from sqlalchemy.orm import Session  # type:ignore

# Infraestructura
from backend.infrastructure.database import get_db
from backend.infrastructure.repositories import (
    SQLAlchemyUserRepository,
    SQLAlchemyIncidentRepository,
    SQLAlchemyTaskRepository,
    SQLAlchemyNotificationRepository
)

# Dominio
from backend.domain.observer import EventBus, NotificationObserver, LogObserver

# DTOs
from backend.application.dtos import (
    IncidentDTO,
    IncidentCreateDTO,
    UserDTO,
    UserCreateDTO,
    LoginDTO,
    TokenDTO,
    TaskCreateDTO,
    TaskDTO,
    NotificationDTO,
)

# Casos de uso
from backend.application.use_cases import (
    IncidentUseCases,
    AuthUseCases,
    TaskUseCases,
    NotificationUseCases
)

# Dependencias de seguridad
from backend.api.dependencies import (
    get_current_user,
    require_admin,
    require_supervisor
)

router = APIRouter()



# PROVEEDORES DE SERVICIOS


def get_auth_service(db: Session = Depends(get_db)):
    repo = SQLAlchemyUserRepository(db)
    return AuthUseCases(repo)


def get_incident_service(db: Session = Depends(get_db)):
    incident_repo = SQLAlchemyIncidentRepository(db)
    user_repo = SQLAlchemyUserRepository(db)
    notification_repo = SQLAlchemyNotificationRepository(db)

    event_bus = EventBus()
    event_bus.subscribe(NotificationObserver(notification_repo))
    event_bus.subscribe(LogObserver())

    return IncidentUseCases(incident_repo, user_repo, event_bus)


def get_task_service(db: Session = Depends(get_db)):
    task_repo = SQLAlchemyTaskRepository(db)
    notification_repo = SQLAlchemyNotificationRepository(db)

    event_bus = EventBus()
    event_bus.subscribe(NotificationObserver(notification_repo))
    event_bus.subscribe(LogObserver())

    return TaskUseCases(task_repo, event_bus)


def get_notification_service(db: Session = Depends(get_db)):
    repo = SQLAlchemyNotificationRepository(db)
    return NotificationUseCases(repo)



# AUTH


@router.post("/auth/register", response_model=UserDTO, status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreateDTO, service: AuthUseCases = Depends(get_auth_service)):
    try:
        return service.register_user(user_data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/auth/login", response_model=TokenDTO)
def login(user_data: LoginDTO, service: AuthUseCases = Depends(get_auth_service)):
    """Recibe email + password, devuelve access_token."""
    try:
        return service.login(user_data)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas"
        )


@router.get("/me", response_model=UserDTO)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Devuelve id, email y role reales del usuario autenticado."""
    return UserDTO(
        id=current_user.id,
        name=getattr(current_user, "name", None),
        email=getattr(current_user, "email", None),
        role=current_user.role,
    )



# INCIDENTES


@router.post("/incidents", response_model=IncidentDTO, status_code=status.HTTP_201_CREATED)
def create_incident(
    incident_data: IncidentCreateDTO,
    current_user: User = Depends(get_current_user),
    service: IncidentUseCases = Depends(get_incident_service)
):
    return service.create_incident(incident_data, current_user.id)


@router.get("/incidents", response_model=List[IncidentDTO])
def list_incidents(
    current_user: User = Depends(get_current_user),
    service: IncidentUseCases = Depends(get_incident_service)
):
    return service.get_all_incidents(current_user)


@router.get("/incidents/{incident_id}", response_model=IncidentDTO)
def get_incident_detail(
    incident_id: str,
    current_user: User = Depends(get_current_user),
    service: IncidentUseCases = Depends(get_incident_service)
):
    incident = service.get_incident_detail(incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incidente no encontrado")
    return incident


@router.patch("/incidents/{incident_id}/assign/{user_id}", response_model=IncidentDTO)
def assign_incident(
    incident_id: str,
    user_id: str,
    current_user: User = Depends(require_supervisor),
    service: IncidentUseCases = Depends(get_incident_service)
):
    return service.assign_incident(incident_id, user_id)


@router.patch("/incidents/{incident_id}/status", response_model=IncidentDTO)
def change_incident_status(
    incident_id: str,
    new_status: str,
    current_user: User = Depends(get_current_user),
    service: IncidentUseCases = Depends(get_incident_service)
):
    """Cualquier usuario autenticado puede avanzar el estado de un incidente."""
    return service.change_status(incident_id, new_status)


@router.delete("/incidents/{incident_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_incident(
    incident_id: str,
    current_user: User = Depends(require_admin),
    service: IncidentUseCases = Depends(get_incident_service)
):
    service.delete_incident(incident_id)
    return None



# TAREAS


@router.post("/tasks", status_code=status.HTTP_201_CREATED)
def create_task(
    task_data: TaskCreateDTO,
    current_user: User = Depends(get_current_user),
    service: TaskUseCases = Depends(get_task_service)
):
    return service.create_task(task_data)


@router.get("/tasks")
def get_tasks(
    current_user: User = Depends(get_current_user),
    service: TaskUseCases = Depends(get_task_service)
):
    return service.get_tasks(current_user)


@router.patch("/tasks/{task_id}/status")
def change_task_status(
    task_id: str,
    new_status: str,
    current_user: User = Depends(get_current_user),
    service: TaskUseCases = Depends(get_task_service)
):
    return service.change_status(task_id, new_status)



# NOTIFICACIONES


@router.get("/notifications")
def get_notifications(
    current_user: User = Depends(get_current_user),
    service: NotificationUseCases = Depends(get_notification_service)
):
    return service.get_notifications(current_user)