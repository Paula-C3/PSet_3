import pytest
from fastapi.testclient import TestClient
from backend.api.routes import router
from fastapi import FastAPI

# Creamos una instancia pequeña de FastAPI para el test
app = FastAPI()
app.include_router(router)
client = TestClient(app)

def test_login_endpoint_exists():
    # Validamos que el endpoint de login responda (aunque sea con error de datos)
    # Esto confirma que la ruta esta bien registrada
    response = client.post("/auth/login", json={})
    assert response.status_code == 422 # Unprocessable Entity (porque enviamos json vacio)

def test_incidents_list_unauthorized():
    # Validamos que no permita ver incidentes sin token (Error 401)
    response = client.get("/incidents")
    assert response.status_code == 401

def test_delete_incident_permissions():
    # Validamos que una ruta protegida devuelva 401 si no hay token
    # (Luego el Guard de Admin lanzaria 403 si el token no es de Admin)
    response = client.delete("/incidents/1")
    assert response.status_code == 401

def test_register_endpoint_structure():
    # Verificamos que el registro pida los campos correctos
    response = client.post("/auth/register", json={"username": "testuser"})
    assert response.status_code == 422 # Falta el password, debe fallar validacion