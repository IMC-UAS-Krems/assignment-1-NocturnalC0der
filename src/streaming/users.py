from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from streaming.sessions import ListeningSession


class User:
    """Base class for all platform users."""

    def __init__(self, user_id: str, name: str, age: int) -> None:
        self.user_id = user_id
        self.name = name
        self.age = age
        self.sessions = []

    def add_session(self, session: ListeningSession) -> None:
        self.sessions.append(session)

    def total_listening_seconds(self) -> int:
        return sum(session.duration_listened_seconds for session in self.sessions)

    def total_listening_minutes(self) -> float:
        return self.total_listening_seconds() / 60

    def unique_tracks_listened(self) -> set[str]:
        track_ids = set()
        for session in self.sessions:
            track_ids.add(session.track.track_id)
        return track_ids


class FreeUser(User):
    """A user on the free tier."""

    MAX_SKIPS_PER_HOUR = 6


class PremiumUser(User):
    """A paying subscriber with full platform access."""

    def __init__(self, user_id: str, name: str, age: int, subscription_start: date) -> None:
        super().__init__(user_id, name, age)
        self.subscription_start = subscription_start


class FamilyAccountUser(User):
    """A primary family account holder who manages sub-users."""

    def __init__(self, user_id: str, name: str, age: int) -> None:
        super().__init__(user_id, name, age)
        self.sub_users = []

    def add_sub_user(self, sub_user: FamilyMember) -> None:
        if sub_user not in self.sub_users:
            self.sub_users.append(sub_user)

    def all_members(self) -> list[User]:
        return [self, *self.sub_users]


class FamilyMember(User):
    """A profile that belongs to a family account."""

    def __init__(self, user_id: str, name: str, age: int, parent: FamilyAccountUser) -> None:
        super().__init__(user_id, name, age)
        self.parent = parent
