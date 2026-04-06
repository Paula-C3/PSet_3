import json
import os

import requests
from typing import Dict, Optional, List, Any

class APIClient:
    """Cliente HTTP para interactuar con la API del backend"""

    def __init__(self, base_url: Optional[str] = None):
        env_url = os.getenv("API_BASE_URL")
        self.base_url = (base_url or env_url or "http://localhost:8000").rstrip('/')
        self._token: Optional[str] = None

    def set_token(self, token: str) -> None:
        """Establece el token de autenticación"""
        self._token = token

    def clear_token(self) -> None:
        """Limpia el token de autenticación"""
        self._token = None

    def _get_headers(self) -> Dict[str, str]:
        """Retorna headers con token si está disponible"""
        headers = {"Content-Type": "application/json"}
        if self._token:
            headers["Authorization"] = f"Bearer {self._token}"
        return headers

    def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
        """Maneja la respuesta HTTP y lanza excepciones si es necesario"""
        try:
            response.raise_for_status()
            return response.json() if response.text else {}
        except requests.exceptions.HTTPError as e:
            error_msg = f"Error HTTP {response.status_code}"
            try:
                error_data = response.json()
                if "detail" in error_data:
                    error_msg += f": {error_data['detail']}"
            except:
                pass
            raise Exception(error_msg)
        except requests.exceptions.RequestException as e:
            raise Exception(f"Error de conexión: {str(e)}")

    # Autenticación
    def login(self, username: str, password: str) -> Dict[str, Any]:
        """Realiza login y retorna token"""
        url = f"{self.base_url}/auth/login"
        data = {"username": username, "password": password}

        response = requests.post(url, json=data, headers=self._get_headers())
        result = self._handle_response(response)

        if "access_token" in result:
            self.set_token(result["access_token"])

        return result

    def register(self, username: str, email: str, password: str) -> Dict[str, Any]:
        """Registra nuevo usuario"""
        url = f"{self.base_url}/auth/register"
        data = {"username": username, "email": email, "password": password}

        response = requests.post(url, json=data, headers=self._get_headers())
        return self._handle_response(response)

    def get_current_user(self) -> Dict[str, Any]:
        """Obtiene información del usuario actual"""
        url = f"{self.base_url}/me"

        response = requests.get(url, headers=self._get_headers())
        return self._handle_response(response)

    # Incidentes
    def get_incidents(self) -> List[Dict[str, Any]]:
        """Obtiene lista de incidentes"""
        url = f"{self.base_url}/incidents"

        response = requests.get(url, headers=self._get_headers())
        return self._handle_response(response)      #type:ignore

    def get_incident(self, incident_id: str) -> Dict[str, Any]:
        """Obtiene detalle de un incidente"""
        url = f"{self.base_url}/incidents/{incident_id}"

        response = requests.get(url, headers=self._get_headers())
        return self._handle_response(response)

    def create_incident(self, title: str, description: str, severity: str) -> Dict[str, Any]:
        """Crea nuevo incidente"""
        url = f"{self.base_url}/incidents"
        data = {
            "title": title,
            "description": description,
            "severity": severity
        }

        response = requests.post(url, json=data, headers=self._get_headers())
        return self._handle_response(response)

    def assign_incident(self, incident_id: str, user_id: str) -> Dict[str, Any]:
        """Asigna incidente a usuario"""
        url = f"{self.base_url}/incidents/{incident_id}/assign/{user_id}"

        response = requests.patch(url, headers=self._get_headers())
        return self._handle_response(response)

    def change_incident_status(self, incident_id: str, new_status: str) -> Dict[str, Any]:
        url = f"{self.base_url}/incidents/{incident_id}/status"
        response = requests.patch(url, params={"new_status": new_status}, headers=self._get_headers())
        return self._handle_response(response)

    def delete_incident(self, incident_id: str) -> Dict[str, Any]:
        """Elimina incidente (solo admin)"""
        url = f"{self.base_url}/incidents/{incident_id}"

        response = requests.delete(url, headers=self._get_headers())
        return self._handle_response(response)

    # Tareas
    def get_tasks(self) -> Any:
        url = f"{self.base_url}/tasks"
        response = requests.get(url, headers=self._get_headers())
        return self._handle_response(response)

    def create_task(self, incident_id: str, title: str, description: str, assigned_to: str) -> Dict[str, Any]:
        """Crea nueva tarea"""
        url = f"{self.base_url}/tasks"
        data = {
            "incident_id": incident_id,
            "title": title,
            "description": description,
            "assigned_to": assigned_to
        }

        response = requests.post(url, json=data, headers=self._get_headers())
        return self._handle_response(response)

    def change_task_status(self, task_id: str, new_status: str) -> Dict[str, Any]:
        url = f"{self.base_url}/tasks/{task_id}/status"
        response = requests.patch(url, params={"new_status": new_status}, headers=self._get_headers())
        return self._handle_response(response)

    # Notificaciones
    def get_notifications(self) -> List[Dict[str, Any]]:
        """Obtiene lista de notificaciones del usuario"""
        url = f"{self.base_url}/notifications"

        response = requests.get(url, headers=self._get_headers())
        return self._handle_response(response)      #type:ignore