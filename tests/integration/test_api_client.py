import pytest
from unittest.mock import Mock, patch
from frontend.api_client import APIClient

class TestAPIClient:
    """Tests para el cliente HTTP de la API"""

    def setup_method(self):
        """Configura el cliente para cada test"""
        self.client = APIClient("http://test-api.com")

    def test_initialization(self):
        """Verifica que el cliente se inicializa correctamente"""
        assert self.client.base_url == "http://test-api.com"
        assert self.client._token is None

    def test_set_token(self):
        """Verifica que se puede establecer el token"""
        self.client.set_token("test-token")
        assert self.client._token == "test-token"

    def test_clear_token(self):
        """Verifica que se puede limpiar el token"""
        self.client.set_token("test-token")
        self.client.clear_token()
        assert self.client._token is None

    def test_get_headers_without_token(self):
        """Verifica headers sin token de autenticación"""
        headers = self.client._get_headers()
        assert headers == {"Content-Type": "application/json"}

    def test_get_headers_with_token(self):
        """Verifica headers con token de autenticación"""
        self.client.set_token("test-token")
        headers = self.client._get_headers()
        expected = {
            "Content-Type": "application/json",
            "Authorization": "Bearer test-token"
        }
        assert headers == expected

    @patch('frontend.api_client.requests.post')
    def test_login_success(self, mock_post):
        """Verifica login exitoso"""
        # Mock response
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {"access_token": "test-token"}
        mock_post.return_value = mock_response

        result = self.client.login("user@test.com", "password")

        assert result == {"access_token": "test-token"}
        assert self.client._token == "test-token"
        mock_post.assert_called_once()

    @patch('frontend.api_client.requests.post')
    def test_login_failure(self, mock_post):
        """Verifica manejo de error en login"""
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = Exception("Invalid credentials")
        mock_post.return_value = mock_response

        with pytest.raises(Exception, match="Invalid credentials"):
            self.client.login("user@test.com", "wrong-password")

    @patch('frontend.api_client.requests.get')
    def test_get_current_user(self, mock_get):
        """Verifica obtención de usuario actual"""
        self.client.set_token("test-token")

        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {"id": "123", "email": "user@test.com"}
        mock_get.return_value = mock_response

        result = self.client.get_current_user()

        assert result == {"id": "123", "email": "user@test.com"}
        mock_get.assert_called_once_with(
            "http://test-api.com/me",
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer test-token"
            }
        )

    @patch('frontend.api_client.requests.get')
    def test_get_incidents(self, mock_get):
        """Verifica obtención de incidentes"""
        self.client.set_token("test-token")

        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = [
            {"id": "1", "title": "Test Incident", "status": "OPEN"}
        ]
        mock_get.return_value = mock_response

        result = self.client.get_incidents()

        assert result == [{"id": "1", "title": "Test Incident", "status": "OPEN"}]
        mock_get.assert_called_once()

    @patch('frontend.api_client.requests.post')
    def test_create_incident(self, mock_post):
        """Verifica creación de incidente"""
        self.client.set_token("test-token")

        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {"id": "123", "title": "New Incident"}
        mock_post.return_value = mock_response

        result = self.client.create_incident("Test", "Description", "HIGH")

        assert result == {"id": "123", "title": "New Incident"}
        mock_post.assert_called_once()

    @patch('frontend.api_client.requests.patch')
    def test_change_incident_status(self, mock_patch):
        """Verifica cambio de estado de incidente"""
        self.client.set_token("test-token")

        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {"id": "123", "status": "RESOLVED"}
        mock_patch.return_value = mock_response

        result = self.client.change_incident_status("123", "RESOLVED")

        assert result == {"id": "123", "status": "RESOLVED"}
        mock_patch.assert_called_once()

    @patch('frontend.api_client.requests.get')
    def test_get_tasks(self, mock_get):
        """Verifica obtención de tareas"""
        self.client.set_token("test-token")

        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = [
            {"id": "1", "title": "Test Task", "status": "OPEN"}
        ]
        mock_get.return_value = mock_response

        result = self.client.get_tasks()

        assert result == [{"id": "1", "title": "Test Task", "status": "OPEN"}]
        mock_get.assert_called_once()

    @patch('frontend.api_client.requests.post')
    def test_create_task(self, mock_post):
        """Verifica creación de tarea"""
        self.client.set_token("test-token")

        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {"id": "456", "title": "New Task"}
        mock_post.return_value = mock_response

        result = self.client.create_task("123", "Test Task", "Description", "user-1")

        assert result == {"id": "456", "title": "New Task"}
        mock_post.assert_called_once()

    @patch('frontend.api_client.requests.patch')
    def test_change_task_status(self, mock_patch):
        """Verifica cambio de estado de tarea"""
        self.client.set_token("test-token")

        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {"id": "456", "status": "DONE"}
        mock_patch.return_value = mock_response

        result = self.client.change_task_status("456", "DONE")

        assert result == {"id": "456", "status": "DONE"}
        mock_patch.assert_called_once()

    @patch('frontend.api_client.requests.get')
    def test_get_notifications(self, mock_get):
        """Verifica obtención de notificaciones"""
        self.client.set_token("test-token")

        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = [
            {"id": "1", "message": "Test notification", "status": "PENDING"}
        ]
        mock_get.return_value = mock_response

        result = self.client.get_notifications()

        assert result == [{"id": "1", "message": "Test notification", "status": "PENDING"}]
        mock_get.assert_called_once()