from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional

from backend.domain.entities import Incident, Notification, Task, User
from backend.domain.enums import IncidentStatus, NotificationStatus, TaskStatus


class UserRepository(ABC):

    @abstractmethod
    def save(self, user: User) -> User:
        ...

    @abstractmethod
    def find_by_id(self, user_id: str) -> Optional[User]:
        ...

    @abstractmethod
    def find_by_email(self, email: str) -> Optional[User]:
        ...

    @abstractmethod
    def find_all(self) -> list[User]:
        ...


class IncidentRepository(ABC):

    @abstractmethod
    def save(self, incident: Incident) -> Incident:
        ...

    @abstractmethod
    def find_by_id(self, incident_id: str) -> Optional[Incident]:
        ...

    @abstractmethod
    def find_all(self) -> list[Incident]:
        ...

    @abstractmethod
    def find_by_creator(self, user_id: str) -> list[Incident]:
        ...

    @abstractmethod
    def find_by_assignee(self, user_id: str) -> list[Incident]:
        ...

    @abstractmethod
    def find_by_status(self, status: IncidentStatus) -> list[Incident]:
        ...


class TaskRepository(ABC):

    @abstractmethod
    def save(self, task: Task) -> Task:
        ...

    @abstractmethod
    def find_by_id(self, task_id: str) -> Optional[Task]:
        ...

    @abstractmethod
    def find_all(self) -> list[Task]:
        ...

    @abstractmethod
    def find_by_incident(self, incident_id: str) -> list[Task]:
        ...

    @abstractmethod
    def find_by_assignee(self, user_id: str) -> list[Task]:
        ...

    @abstractmethod
    def find_by_status(self, status: TaskStatus) -> list[Task]:
        ...


class NotificationRepository(ABC):

    @abstractmethod
    def save(self, notification: Notification) -> Notification:
        ...

    @abstractmethod
    def find_by_id(self, notification_id: str) -> Optional[Notification]:
        ...

    @abstractmethod
    def find_by_recipient(self, user_id: str) -> list[Notification]:
        ...

    @abstractmethod
    def find_all(self) -> list[Notification]:
        ...

    @abstractmethod
    def find_by_status(self, status: NotificationStatus) -> list[Notification]:
        ...