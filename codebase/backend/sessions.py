from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from threading import Lock
from uuid import uuid4


VALID_LEVELS = {"coban", "thongthao", "nangcao"}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class TutorSession:
    session_id: str
    level: str = "coban"
    correct_streak: int = 0
    incorrect_streak: int = 0
    evidence_topics: list[str] = field(default_factory=list)
    created_at: str = field(default_factory=utc_now)
    updated_at: str = field(default_factory=utc_now)

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


class SessionStore:
    """Thread-safe in-memory session state for the MVP."""

    def __init__(self) -> None:
        self._sessions: dict[str, TutorSession] = {}
        self._lock = Lock()

    def create(self, initial_level: str = "coban") -> TutorSession:
        if initial_level not in VALID_LEVELS:
            raise ValueError("initial_level must be coban, thongthao, or nangcao")
        session = TutorSession(session_id=uuid4().hex, level=initial_level)
        with self._lock:
            self._sessions[session.session_id] = session
        return session

    def get(self, session_id: str) -> TutorSession | None:
        with self._lock:
            return self._sessions.get(session_id)

    def set_level(self, session_id: str, level: str) -> TutorSession | None:
        if level not in VALID_LEVELS:
            raise ValueError("level must be coban, thongthao, or nangcao")
        with self._lock:
            session = self._sessions.get(session_id)
            if session:
                session.level = level
                session.updated_at = utc_now()
            return session
