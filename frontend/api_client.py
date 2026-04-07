import requests
from typing import Optional, List, Dict, Any


class APIClient:
    """Cliente HTTP para interactuar con la API backend"""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip("/")
        self._token: Optional[str] = None

    def set_token(self, token: str):
        self._token = token

    def clear_token(self):
        self._token = None

    def _headers(self) -> Dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self._token:
            headers["Authorization"] = f"Bearer {self._token}"
        return headers

    def login(self, email: str, password: str) -> Dict[str, Any]:
        response = requests.post(
            f"{self.base_url}/auth/login",
            json={"email": email, "password": password},
            timeout=10,
        )
        response.raise_for_status()
        return response.json()

    def get_me(self) -> Dict[str, Any]:
        response = requests.get(
            f"{self.base_url}/me",
            headers=self._headers(),
            timeout=10,
        )
        response.raise_for_status()
        return response.json()

    def get_users(self) -> List[Dict[str, Any]]:
        response = requests.get(
            f"{self.base_url}/users",
            headers=self._headers(),
            timeout=10,
        )
        response.raise_for_status()
        return response.json()

    def register(self, name: str, email: str, password: str, role: str = "OPERATOR") -> Dict[str, Any]:
        response = requests.post(
            f"{self.base_url}/auth/register",
            json={"name": name, "email": email, "password": password, "role": role},
            timeout=10,
        )
        response.raise_for_status()
        return response.json()

    def get_incidents(self) -> List[Dict[str, Any]]:
        response = requests.get(
            f"{self.base_url}/incidents",
            headers=self._headers(),
            timeout=10,
        )
        response.raise_for_status()
        return response.json()

    def get_incident(self, incident_id: str) -> Dict[str, Any]:
        response = requests.get(
            f"{self.base_url}/incidents/{incident_id}",
            headers=self._headers(),
            timeout=10,
        )
        response.raise_for_status()
        return response.json()

    def create_incident(self, title: str, description: str, severity: str) -> Dict[str, Any]:
        response = requests.post(
            f"{self.base_url}/incidents",
            json={"title": title, "description": description, "severity": severity},
            headers=self._headers(),
            timeout=10,
        )
        response.raise_for_status()
        return response.json()

    def assign_incident(self, incident_id: str, user_id: str) -> Dict[str, Any]:
        response = requests.patch(
            f"{self.base_url}/incidents/{incident_id}/assign/{user_id}",
            headers=self._headers(),
            timeout=10,
        )
        response.raise_for_status()
        return response.json()

    def change_incident_status(self, incident_id: str, new_status: str) -> Dict[str, Any]:
        response = requests.patch(
            f"{self.base_url}/incidents/{incident_id}/status",
            params={"new_status": new_status},
            headers=self._headers(),
            timeout=10,
        )
        response.raise_for_status()
        return response.json()

    def delete_incident(self, incident_id: str) -> None:
        response = requests.delete(
            f"{self.base_url}/incidents/{incident_id}",
            headers=self._headers(),
            timeout=10,
        )
        response.raise_for_status()

    def get_tasks(self) -> List[Dict[str, Any]]:
        response = requests.get(
            f"{self.base_url}/tasks",
            headers=self._headers(),
            timeout=10,
        )
        response.raise_for_status()
        return response.json()

    def create_task(self, incident_id: str, title: str, description: str, assigned_to: str) -> Dict[str, Any]:
        response = requests.post(
            f"{self.base_url}/tasks",
            json={
                "incident_id": incident_id,
                "title": title,
                "description": description,
                "assigned_to": assigned_to,
            },
            headers=self._headers(),
            timeout=10,
        )
        response.raise_for_status()
        return response.json()

    def change_task_status(self, task_id: str, new_status: str) -> Dict[str, Any]:
        response = requests.patch(
            f"{self.base_url}/tasks/{task_id}/status",
            params={"new_status": new_status},
            headers=self._headers(),
            timeout=10,
        )
        response.raise_for_status()
        return response.json()

    def get_notifications(self) -> List[Dict[str, Any]]:
        response = requests.get(
            f"{self.base_url}/notifications",
            headers=self._headers(),
            timeout=10,
        )
        response.raise_for_status()
        return response.json()
