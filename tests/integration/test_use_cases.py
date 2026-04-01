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
    assert bus.publish.called, "El EventBus debe ser notificado" [cite: 90]

def test_login_invalid_credentials_raises_error():
    # Mock de repositorio de usuarios
    user_repo = MagicMock()
    user_repo.find_by_email.return_value = None # Usuario no existe
    
    auth_use_cases = AuthUseCases(user_repo)
    data = LoginRequest(email="test@usfq.edu.ec", password="wrongpassword")
    
    # Verificar que lanza la excepcion correcta
    with pytest.raises(ValueError, match="Credenciales invalidas"):
        auth_use_cases.login(data)