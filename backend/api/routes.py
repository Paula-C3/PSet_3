from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlalchemy.orm import Session

# Importamos la conexión a la base de datos y repositorios
from backend.infrastructure.database import get_db
from backend.infrastructure.repositories import (
    SQLAlchemyUserRepository, 
    SQLAlchemyIncidentRepository
)
from backend.domain.observer import EventBus

# Importamos DTOs y Casos de Uso
from backend.application.dtos import (
    IncidentDTO, IncidentCreateDTO, 
    UserDTO, UserCreateDTO, TokenDTO
)
from backend.application.use_cases import IncidentUseCases, AuthUseCases
from backend.api.dependencies import get_current_user, require_admin, require_supervisor

router = APIRouter()

# --- PROVEEDORES DE SERVICIOS (Dependency Injection) ---

def get_auth_service(db: Session = Depends(get_db)):
    """Instancia el servicio de autenticacion con su repositorio."""
    repo = SQLAlchemyUserRepository(db)
    return AuthUseCases(repo)

def get_incident_service(db: Session = Depends(get_db)):
    """Instancia el servicio de incidentes con sus dependencias."""
    incident_repo = SQLAlchemyIncidentRepository(db)
    user_repo = SQLAlchemyUserRepository(db)
    event_bus = EventBus() # O tu instancia global si existe
    return IncidentUseCases(incident_repo, user_repo, event_bus)

# --- RUTAS DE AUTENTICACION ---

@router.post("/auth/register", response_model=UserDTO, status_code=status.HTTP_201_CREATED)
def register(
    user_data: UserCreateDTO, 
    service: AuthUseCases = Depends(get_auth_service)
):
    return service.register_user(user_data)

@router.post("/auth/login", response_model=TokenDTO)
def login(
    user_data: UserCreateDTO, 
    service: AuthUseCases = Depends(get_auth_service)
):
    token = service.login_user(user_data.username, user_data.password)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Credenciales incorrectas"
        )
    return {"access_token": token, "token_type": "bearer"}

# --- RUTAS DE INCIDENTES ---

@router.post("/incidents", response_model=IncidentDTO, status_code=status.HTTP_201_CREATED)
def create_incident(
    incident_data: IncidentCreateDTO, 
    current_user: dict = Depends(get_current_user),
    service: IncidentUseCases = Depends(get_incident_service)
):
    return service.create_incident(incident_data, current_user["user_id"])

@router.get("/incidents", response_model=List[IncidentDTO])
def list_incidents(
    current_user: dict = Depends(get_current_user),
    service: IncidentUseCases = Depends(get_incident_service)
):
    return service.get_all_incidents()

@router.patch("/incidents/{incident_id}/assign/{user_id}", response_model=IncidentDTO)
def assign_incident(
    incident_id: str, 
    user_id: str,
    current_user: dict = Depends(require_supervisor),
    service: IncidentUseCases = Depends(get_incident_service)
):
    return service.assign_incident(incident_id, user_id)

@router.delete("/incidents/{incident_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_incident(
    incident_id: str,
    current_user: dict = Depends(require_admin),
    service: IncidentUseCases = Depends(get_incident_service)
):
    service.delete_incident(incident_id)
    return None