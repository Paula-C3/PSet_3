from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from backend.domain.enums import IncidentStatus

if TYPE_CHECKING:
    from backend.domain.entities import Incident


class InvalidTransitionError(Exception):
    pass


class IncidentState(ABC):
    @abstractmethod
    def assign(self, incident: Incident, assignee_id: str) -> None:
        ...

    @abstractmethod
    def start_progress(self, incident: Incident) -> None:
        ...

    @abstractmethod
    def resolve(self, incident: Incident) -> None:
        ...

    @abstractmethod
    def close(self, incident: Incident) -> None:
        ...

    def _reject(self, action: str) -> None:
        raise InvalidTransitionError(
            f"Cannot perform '{action}' on an incident in state "
            f"'{self.__class__.__name__}'."
        )


class OpenState(IncidentState):
    def assign(self, incident: Incident, assignee_id: str) -> None:
        incident.assigned_to = assignee_id
        incident.status = IncidentStatus.ASSIGNED
        incident._state = AssignedState()

    def start_progress(self, incident: Incident) -> None:
        self._reject("start_progress")

    def resolve(self, incident: Incident) -> None:
        self._reject("resolve")

    def close(self, incident: Incident) -> None:
        self._reject("close")


class AssignedState(IncidentState):
    def assign(self, incident: Incident, assignee_id: str) -> None:
        incident.assigned_to = assignee_id

    def start_progress(self, incident: Incident) -> None:
        incident.status = IncidentStatus.IN_PROGRESS
        incident._state = InProgressState()

    def resolve(self, incident: Incident) -> None:
        self._reject("resolve")

    def close(self, incident: Incident) -> None:
        self._reject("close")


class InProgressState(IncidentState):
    def assign(self, incident: Incident, assignee_id: str) -> None:
        incident.assigned_to = assignee_id

    def start_progress(self, incident: Incident) -> None:
        self._reject("start_progress")

    def resolve(self, incident: Incident) -> None:
        incident.status = IncidentStatus.RESOLVED
        incident._state = ResolvedState()

    def close(self, incident: Incident) -> None:
        self._reject("close")


class ResolvedState(IncidentState):
    def assign(self, incident: Incident, assignee_id: str) -> None:
        self._reject("assign")

    def start_progress(self, incident: Incident) -> None:
        self._reject("start_progress")

    def resolve(self, incident: Incident) -> None:
        self._reject("resolve")

    def close(self, incident: Incident) -> None:
        incident.status = IncidentStatus.CLOSED
        incident._state = ClosedState()


class ClosedState(IncidentState):
    def assign(self, incident: Incident, assignee_id: str) -> None:
        self._reject("assign")

    def start_progress(self, incident: Incident) -> None:
        self._reject("start_progress")

    def resolve(self, incident: Incident) -> None:
        self._reject("resolve")

    def close(self, incident: Incident) -> None:
        self._reject("close")


_STATUS_TO_STATE: dict[IncidentStatus, IncidentState] = {
    IncidentStatus.OPEN: OpenState(),
    IncidentStatus.ASSIGNED: AssignedState(),
    IncidentStatus.IN_PROGRESS: InProgressState(),
    IncidentStatus.RESOLVED: ResolvedState(),
    IncidentStatus.CLOSED: ClosedState(),
}


def state_for(status: IncidentStatus) -> IncidentState:
    return _STATUS_TO_STATE[status]