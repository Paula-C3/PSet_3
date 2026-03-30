from __future__ import annotations

from sqlalchemy.orm import Session

from domain.entities import User, Incident, Task, Notification
from domain.enums import IncidentStatus, TaskStatus, NotificationStatus
from domain.repositories import (
    UserRepository,
    IncidentRepository,
    TaskRepository,
    NotificationRepository,
)
from infrastructure.models import (
    UserModel,
    IncidentModel,
    TaskModel,
    NotificationModel,
)


def _to_domain_user(model: UserModel) -> User:
    return User(
        id=model.id,
        name=model.name,
        email=model.email,
        hashed_password=model.hashed_password,
        role=model.role,
    )


def _to_domain_incident(model: IncidentModel) -> Incident:
    return Incident(
        id=model.id,
        title=model.title,
        description=model.description,
        severity=model.severity,
        status=model.status,
        created_by=model.created_by,
        assigned_to=model.assigned_to,
        created_at=model.created_at,
    )


def _to_domain_task(model: TaskModel) -> Task:
    return Task(
        id=model.id,
        incident_id=model.incident_id,
        title=model.title,
        description=model.description,
        status=model.status,
        assigned_to=model.assigned_to,
        created_at=model.created_at,
    )


def _to_domain_notification(model: NotificationModel) -> Notification:
    return Notification(
        id=model.id,
        recipient=model.recipient,
        channel=model.channel,
        message=model.message,
        event_type=model.event_type,
        status=model.status,
        created_at=model.created_at,
    )


class SQLAlchemyUserRepository(UserRepository):
    def __init__(self, db: Session):
        self.db = db

    def save(self, user: User) -> User:
        model = self.db.query(UserModel).filter(UserModel.id == user.id).first()

        if model is None:
            model = UserModel(
                id=user.id,
                name=user.name,
                email=user.email,
                hashed_password=user.hashed_password,
                role=user.role,
            )
            self.db.add(model)
        else:
            model.name = user.name
            model.email = user.email
            model.hashed_password = user.hashed_password
            model.role = user.role

        self.db.commit()
        self.db.refresh(model)
        return _to_domain_user(model)

    def find_by_id(self, user_id: str) -> User | None:
        model = self.db.query(UserModel).filter(UserModel.id == user_id).first()
        return _to_domain_user(model) if model else None

    def find_by_email(self, email: str) -> User | None:
        model = self.db.query(UserModel).filter(UserModel.email == email).first()
        return _to_domain_user(model) if model else None

    def find_all(self) -> list[User]:
        models = self.db.query(UserModel).all()
        return [_to_domain_user(model) for model in models]


class SQLAlchemyIncidentRepository(IncidentRepository):
    def __init__(self, db: Session):
        self.db = db

    def save(self, incident: Incident) -> Incident:
        model = self.db.query(IncidentModel).filter(IncidentModel.id == incident.id).first()

        if model is None:
            model = IncidentModel(
                id=incident.id,
                title=incident.title,
                description=incident.description,
                severity=incident.severity,
                status=incident.status,
                created_by=incident.created_by,
                assigned_to=incident.assigned_to,
                created_at=incident.created_at,
            )
            self.db.add(model)
        else:
            model.title = incident.title
            model.description = incident.description
            model.severity = incident.severity
            model.status = incident.status
            model.created_by = incident.created_by
            model.assigned_to = incident.assigned_to
            model.created_at = incident.created_at

        self.db.commit()
        self.db.refresh(model)
        return _to_domain_incident(model)

    def find_by_id(self, incident_id: str) -> Incident | None:
        model = self.db.query(IncidentModel).filter(IncidentModel.id == incident_id).first()
        return _to_domain_incident(model) if model else None

    def find_all(self) -> list[Incident]:
        models = self.db.query(IncidentModel).all()
        return [_to_domain_incident(model) for model in models]

    def find_by_creator(self, user_id: str) -> list[Incident]:
        models = self.db.query(IncidentModel).filter(IncidentModel.created_by == user_id).all()
        return [_to_domain_incident(model) for model in models]

    def find_by_assignee(self, user_id: str) -> list[Incident]:
        models = self.db.query(IncidentModel).filter(IncidentModel.assigned_to == user_id).all()
        return [_to_domain_incident(model) for model in models]

    def find_by_status(self, status: IncidentStatus) -> list[Incident]:
        models = self.db.query(IncidentModel).filter(IncidentModel.status == status).all()
        return [_to_domain_incident(model) for model in models]


class SQLAlchemyTaskRepository(TaskRepository):
    def __init__(self, db: Session):
        self.db = db

    def save(self, task: Task) -> Task:
        model = self.db.query(TaskModel).filter(TaskModel.id == task.id).first()

        if model is None:
            model = TaskModel(
                id=task.id,
                incident_id=task.incident_id,
                title=task.title,
                description=task.description,
                status=task.status,
                assigned_to=task.assigned_to,
                created_at=task.created_at,
            )
            self.db.add(model)
        else:
            model.incident_id = task.incident_id
            model.title = task.title
            model.description = task.description
            model.status = task.status
            model.assigned_to = task.assigned_to
            model.created_at = task.created_at

        self.db.commit()
        self.db.refresh(model)
        return _to_domain_task(model)

    def find_by_id(self, task_id: str) -> Task | None:
        model = self.db.query(TaskModel).filter(TaskModel.id == task_id).first()
        return _to_domain_task(model) if model else None

    def find_all(self) -> list[Task]:
        models = self.db.query(TaskModel).all()
        return [_to_domain_task(model) for model in models]

    def find_by_incident(self, incident_id: str) -> list[Task]:
        models = self.db.query(TaskModel).filter(TaskModel.incident_id == incident_id).all()
        return [_to_domain_task(model) for model in models]

    def find_by_assignee(self, user_id: str) -> list[Task]:
        models = self.db.query(TaskModel).filter(TaskModel.assigned_to == user_id).all()
        return [_to_domain_task(model) for model in models]

    def find_by_status(self, status: TaskStatus) -> list[Task]:
        models = self.db.query(TaskModel).filter(TaskModel.status == status).all()
        return [_to_domain_task(model) for model in models]


class SQLAlchemyNotificationRepository(NotificationRepository):
    def __init__(self, db: Session):
        self.db = db

    def save(self, notification: Notification) -> Notification:
        model = self.db.query(NotificationModel).filter(NotificationModel.id == notification.id).first()

        if model is None:
            model = NotificationModel(
                id=notification.id,
                recipient=notification.recipient,
                channel=notification.channel,
                message=notification.message,
                event_type=notification.event_type,
                status=notification.status,
                created_at=notification.created_at,
            )
            self.db.add(model)
        else:
            model.recipient = notification.recipient
            model.channel = notification.channel
            model.message = notification.message
            model.event_type = notification.event_type
            model.status = notification.status
            model.created_at = notification.created_at

        self.db.commit()
        self.db.refresh(model)
        return _to_domain_notification(model)

    def find_by_id(self, notification_id: str) -> Notification | None:
        model = self.db.query(NotificationModel).filter(NotificationModel.id == notification_id).first()
        return _to_domain_notification(model) if model else None

    def find_by_recipient(self, user_id: str) -> list[Notification]:
        models = self.db.query(NotificationModel).filter(NotificationModel.recipient == user_id).all()
        return [_to_domain_notification(model) for model in models]

    def find_all(self) -> list[Notification]:
        models = self.db.query(NotificationModel).all()
        return [_to_domain_notification(model) for model in models]

    def find_by_status(self, status: NotificationStatus) -> list[Notification]:
        models = self.db.query(NotificationModel).filter(NotificationModel.status == status).all()
        return [_to_domain_notification(model) for model in models]