from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from streaming.tracks import Track


class Artist:
    """Represents a music artist or content creator."""

    def __init__(self, artist_id: str, name: str, genre: str) -> None:
        self.artist_id = artist_id
        self.name = name
        self.genre = genre
        self.tracks = []

    def add_track(self, track: Track) -> None:
        """Add a track to the artist's catalogue."""
        self.tracks.append(track)

    def track_count(self) -> int:
        """Return the number of tracks by this artist."""
        return len(self.tracks)
