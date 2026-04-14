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
# #registro de usuario 


@router.post("/auth/register", response_model=UserDTO, status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreateDTO, service: AuthUseCases = Depends(get_auth_service)):
    try:
        return service.register_user(user_data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# login de usuario devuelve un token JWT con id, email y role del usuario para autenticacion en futuras solicitudes
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

#aqui creamos incidentes, listamos incidentes, obtenemos detalle de un incidente, asignamos un incidente a un usuario, cambiamos el estado de un incidente y eliminamos un incidente. Solo usuarios autenticados pueden crear y listar incidentes. Solo SUPERVISOR y ADMIN pueden cambiar el estado de un incidente. Solo ADMIN puede asignar incidentes y eliminar incidentes.
@router.post("/incidents", response_model=IncidentDTO, status_code=status.HTTP_201_CREATED)
def create_incident(
    incident_data: IncidentCreateDTO,
    current_user: User = Depends(get_current_user),
    service: IncidentUseCases = Depends(get_incident_service)
):
    return service.create_incident(incident_data, current_user.id)

# Listar incidentes devuelve solo los incidentes creados por el usuario autenticado o asignados a él. Usuarios con rol SUPERVISOR o ADMIN pueden ver todos los incidentes.
@router.get("/incidents", response_model=List[IncidentDTO])
def list_incidents(
    current_user: User = Depends(get_current_user),
    service: IncidentUseCases = Depends(get_incident_service)
):
    return service.get_all_incidents(current_user)

# Obtener detalle de un incidente devuelve toda la información del incidente, incluyendo comentarios y tareas asociadas. Solo usuarios autenticados pueden acceder a esta ruta. Usuarios con rol SUPERVISOR o ADMIN pueden acceder a cualquier incidente, mientras que usuarios con rol USER solo pueden acceder a incidentes que hayan creado o que les hayan sido asignados.
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

# Asignar incidente a un usuario específico. Solo usuarios con rol ADMIN pueden asignar incidentes a otros usuarios.
@router.patch("/incidents/{incident_id}/assign/{user_id}", response_model=IncidentDTO)
def assign_incident(
    incident_id: str,
    user_id: str,
    current_user: User = Depends(require_admin),
    service: IncidentUseCases = Depends(get_incident_service)
):
    return service.assign_incident(incident_id, user_id)

# Cambiar estado de un incidente. Solo usuarios con rol SUPERVISOR o ADMIN pueden cambiar el estado de un incidente. Usuarios con rol USER no tienen permiso para cambiar el estado de un incidente, incluso si son los creadores o asignados del incidente.
@router.patch("/incidents/{incident_id}/status", response_model=IncidentDTO)
def change_incident_status(
    incident_id: str,
    new_status: str,
    current_user: User = Depends(require_supervisor),
    service: IncidentUseCases = Depends(get_incident_service)
):
    """Solo SUPERVISOR y ADMIN pueden cambiar el estado de un incidente."""
    return service.change_status(incident_id, new_status)

# Eliminar un incidente. Solo usuarios con rol ADMIN pueden eliminar incidentes. Usuarios con rol USER o SUPERVISOR no tienen permiso para eliminar incidentes, incluso si son los creadores o asignados del incidente.
@router.delete("/incidents/{incident_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_incident(
    incident_id: str,
    current_user: User = Depends(require_admin),
    service: IncidentUseCases = Depends(get_incident_service)
):
    service.delete_incident(incident_id)
    return None



# TAREAS

# Crear una tarea asociada a un incidente específico. Solo usuarios autenticados pueden crear tareas. El creador de la tarea se establece automáticamente como el usuario autenticado que realiza la solicitud. El estado inicial de la tarea es "pendiente".
@router.post("/tasks", status_code=status.HTTP_201_CREATED)
def create_task(
    task_data: TaskCreateDTO,
    current_user: User = Depends(get_current_user),
    service: TaskUseCases = Depends(get_task_service)
):
    return service.create_task(task_data)

# Listar tareas devuelve solo las tareas creadas por el usuario autenticado o asignadas a él. Usuarios con rol SUPERVISOR o ADMIN pueden ver todas las tareas.
@router.get("/tasks")
def get_tasks(
    current_user: User = Depends(get_current_user),
    service: TaskUseCases = Depends(get_task_service)
):
    return service.get_tasks(current_user)

# Cambiar estado de una tarea. Solo usuarios con rol SUPERVISOR o ADMIN pueden cambiar el estado de una tarea. Usuarios con rol USER no tienen permiso para cambiar el estado de una tarea, incluso si son los creadores o asignados de la tarea.
@router.patch("/tasks/{task_id}/status")
def change_task_status(
    task_id: str,
    new_status: str,
    current_user: User = Depends(get_current_user),
    service: TaskUseCases = Depends(get_task_service)
):
    return service.change_status(task_id, new_status)



# NOTIFICACIONES

# Listar notificaciones devuelve solo las notificaciones del usuario autenticado. Usuarios con rol SUPERVISOR o ADMIN pueden ver todas sus notificaciones, pero no las de otros usuarios.
@router.get("/notifications")
def get_notifications(
    current_user: User = Depends(get_current_user),
    service: NotificationUseCases = Depends(get_notification_service)
):
    return service.get_notifications(current_user)