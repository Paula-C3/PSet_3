from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.infrastructure.database import Base
from backend.infrastructure.repositories import (
    SQLAlchemyUserRepository,
    SQLAlchemyIncidentRepository,
    SQLAlchemyTaskRepository,
    SQLAlchemyNotificationRepository,
)
from backend.domain.entities import User, Incident, Task, Notification
from backend.domain.enums import (
    Role,
    Severity,
    IncidentStatus,
    TaskStatus,
    EventType,
    NotificationChannel,
    NotificationStatus,
)


SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def setup_function():
    Base.metadata.create_all(bind=engine)


def teardown_function():
    Base.metadata.drop_all(bind=engine)


def test_user_repository_save_and_find():
    db = TestingSessionLocal()
    repo = SQLAlchemyUserRepository(db)

    user = User(
        name="Juan",
        email="juan@test.com",
        password="hashed123",
        role=Role.ADMIN,
    )

    saved = repo.save(user)
    found = repo.find_by_id(saved.id)

    assert found is not None
    assert found.email == "juan@test.com"
    assert found.role == Role.ADMIN

    db.close()


def test_user_repository_find_by_email():
    db = TestingSessionLocal()
    repo = SQLAlchemyUserRepository(db)

    user = User(
        name="Ana",
        email="ana@test.com",
        password="hashed456",
        role=Role.OPERATOR,
    )
    repo.save(user)

    found = repo.find_by_email("ana@test.com")

    assert found is not None
    assert found.name == "Ana"

    db.close()


def test_incident_repository_save_and_find_by_creator():
    db = TestingSessionLocal()

    user_repo = SQLAlchemyUserRepository(db)
    incident_repo = SQLAlchemyIncidentRepository(db)

    user = User(
        name="Carlos",
        email="carlos@test.com",
        password="hashed789",
        role=Role.OPERATOR,
    )
    saved_user = user_repo.save(user)

    incident = Incident(
        title="Server down",
        description="Main server is not responding",
        severity=Severity.HIGH,
        created_by=saved_user.id,
    )
    saved_incident = incident_repo.save(incident)

    found = incident_repo.find_by_id(saved_incident.id)
    by_creator = incident_repo.find_by_creator(saved_user.id)

    assert found is not None
    assert found.title == "Server down"
    assert len(by_creator) == 1
    assert by_creator[0].created_by == saved_user.id

    db.close()


def test_incident_repository_find_by_status():
    db = TestingSessionLocal()

    user_repo = SQLAlchemyUserRepository(db)
    incident_repo = SQLAlchemyIncidentRepository(db)

    user = User(
        name="Maria",
        email="maria@test.com",
        password="hash999",
        role=Role.SUPERVISOR,
    )
    saved_user = user_repo.save(user)

    incident = Incident(
        title="Database issue",
        description="Database connection timeout",
        severity=Severity.CRITICAL,
        created_by=saved_user.id,
        status=IncidentStatus.OPEN,
    )
    incident_repo.save(incident)

    results = incident_repo.find_by_status(IncidentStatus.OPEN)

    assert len(results) == 1
    assert results[0].status == IncidentStatus.OPEN

    db.close()


def test_task_repository_save_and_find_by_incident():
    db = TestingSessionLocal()

    user_repo = SQLAlchemyUserRepository(db)
    incident_repo = SQLAlchemyIncidentRepository(db)
    task_repo = SQLAlchemyTaskRepository(db)

    user = User(
        name="Pedro",
        email="pedro@test.com",
        password="hash111",
        role=Role.OPERATOR,
    )
    saved_user = user_repo.save(user)

    incident = Incident(
        title="Payment bug",
        description="Payments are duplicated",
        severity=Severity.MEDIUM,
        created_by=saved_user.id,
    )
    saved_incident = incident_repo.save(incident)

    task = Task(
        incident_id=saved_incident.id,
        title="Review logs",
        description="Check logs for duplicate transactions",
        assigned_to=saved_user.id,
        status=TaskStatus.OPEN,
    )
    saved_task = task_repo.save(task)

    found = task_repo.find_by_id(saved_task.id)
    by_incident = task_repo.find_by_incident(saved_incident.id)

    assert found is not None
    assert found.title == "Review logs"
    assert len(by_incident) == 1
    assert by_incident[0].incident_id == saved_incident.id

    db.close()


def test_notification_repository_save_and_find_by_recipient():
    db = TestingSessionLocal()

    user_repo = SQLAlchemyUserRepository(db)
    notification_repo = SQLAlchemyNotificationRepository(db)

    user = User(
        name="Luisa",
        email="luisa@test.com",
        password="hash222",
        role=Role.OPERATOR,
    )
    saved_user = user_repo.save(user)

    notification = Notification(
        recipient=saved_user.id,
        channel=NotificationChannel.IN_APP,
        message="Incident assigned to you",
        event_type=EventType.INCIDENT_ASSIGNED,
        status=NotificationStatus.PENDING,
    )
    saved_notification = notification_repo.save(notification)

    found = notification_repo.find_by_id(saved_notification.id)
    by_recipient = notification_repo.find_by_recipient(saved_user.id)

    assert found is not None
    assert found.message == "Incident assigned to you"
    assert len(by_recipient) == 1
    assert by_recipient[0].recipient == saved_user.id

    db.close()