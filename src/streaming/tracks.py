from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from streaming.artists import Artist
    from streaming.albums import Album


class Track:
    """Abstract base class for all playable content."""

    def __init__(self, track_id: str, title: str, duration_seconds: int, genre: str) -> None:
        self.track_id = track_id
        self.title = title
        self.duration_seconds = duration_seconds
        self.genre = genre

    def duration_minutes(self) -> float:
        """Return the duration in minutes."""
        return self.duration_seconds / 60

    def __eq__(self, other: object) -> bool:
        """Compare tracks by ID."""
        if not hasattr(other, "track_id"):
            return False
        return self.track_id == other.track_id


class Song(Track):
    """A song track associated with an artist."""

    def __init__(self, track_id: str, title: str, duration_seconds: int, genre: str, artist: Artist) -> None:
        super().__init__(track_id, title, duration_seconds, genre)
        self.artist = artist


class SingleRelease(Song):
    """A song released as a standalone single."""

    def __init__(self, track_id: str, title: str, duration_seconds: int, genre: str, artist: Artist, release_date: date) -> None:
        super().__init__(track_id, title, duration_seconds, genre, artist)
        self.release_date = release_date


class AlbumTrack(Song):
    """A song track that is part of an album."""

    def __init__(self, track_id: str, title: str, duration_seconds: int, genre: str, artist: Artist, track_number: int) -> None:
        super().__init__(track_id, title, duration_seconds, genre, artist)
        self.track_number = track_number
        self.album = None


class Podcast(Track):
    """A podcast episode."""

    def __init__(self, track_id: str, title: str, duration_seconds: int, genre: str, host: str, description: str = "") -> None:
        super().__init__(track_id, title, duration_seconds, genre)
        self.host = host
        self.description = description


class InterviewEpisode(Podcast):
    """A podcast episode in interview format."""

    def __init__(self, track_id: str, title: str, duration_seconds: int, genre: str, host: str, guest: str, description: str = "") -> None:
        super().__init__(track_id, title, duration_seconds, genre, host, description)
        self.guest = guest


class NarrativeEpisode(Podcast):
    """A podcast episode in narrative format."""

    def __init__(self, track_id: str, title: str, duration_seconds: int, genre: str, host: str, season: int, episode_number: int, description: str = "") -> None:
        super().__init__(track_id, title, duration_seconds, genre, host, description)
        self.season = season
        self.episode_number = episode_number


class AudiobookTrack(Track):
    """A chapter or section from an audiobook."""

    def __init__(self, track_id: str, title: str, duration_seconds: int, genre: str, author: str, narrator: str) -> None:
        super().__init__(track_id, title, duration_seconds, genre)
        self.author = author
        self.narrator = narrator
