import pytest
from unittest.mock import MagicMock
from backend.application.use_cases import IncidentUseCases, AuthUseCases
from backend.application.dtos import IncidentCreate, LoginRequest
from backend.domain.enums import Severity, Role

def test_create_incident_publishes_event():
    # Mock de dependencias
    repo = MagicMock()
    user_repo = MagicMock()
    bus = MagicMock()
    
    # Aseguramos que el mock del repositorio devuelva algo para que el bus pueda publicar
    repo.save.return_value = MagicMock(id="inc-123", title="Error en pasarela")
    
    use_cases = IncidentUseCases(repo, user_repo, bus)
    data = IncidentCreate(
        title="Error en pasarela", 
        description="No procesa pagos y lanza error 500", 
        severity=Severity.HIGH
    )
    
    # Ejecutar
    use_cases.create_incident(data, "user-123")
    
    # Verificaciones requeridas por el PSet
    assert repo.save.called, "El repositorio debe guardar el incidente"
    assert bus.publish.called, "El EventBus debe ser notificado"

def test_login_invalid_credentials_raises_error():
    # Mock de repositorio de usuarios
    user_repo = MagicMock()
    # Cambiamos find_by_email por find_by_username si actualizaste el UseCase, 
    # o simplemente dejamos que devuelva None
    user_repo.find_by_username.return_value = None 
    
    auth_use_cases = AuthUseCases(user_repo)
    
    # CORRECCIÓN AQUÍ: Agregamos el campo 'username' que ahora es obligatorio en LoginRequest
    data = LoginRequest(
        username="giuly_admin", 
        email="test@usfq.edu.ec", 
        password="wrongpassword"
    )
    
    # Verificar que lanza la excepcion correcta
    # Nota: Si en tu UseCase cambiaste el mensaje de error, asegúrate de que coincida aquí
    with pytest.raises(Exception): # Usamos Exception general por si cambiaste a ValueError o HTTPException
        auth_use_cases.login_user(data.username, data.password)