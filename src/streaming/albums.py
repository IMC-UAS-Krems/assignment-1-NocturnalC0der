from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from streaming.artists import Artist
    from streaming.tracks import AlbumTrack


class Album:
    """Represents an album - an ordered collection of tracks by an artist."""

    def __init__(self, album_id: str, title: str, artist: Artist, release_year: int) -> None:
        self.album_id = album_id
        self.title = title
        self.artist = artist
        self.release_year = release_year
        self.tracks = []

    def add_track(self, track: AlbumTrack) -> None:
        """Add a track to the album and set the track's album reference."""
        track.album = self
        self.tracks.append(track)
        # Sort tracks by track_number
        self.tracks.sort(key=lambda t: t.track_number)

    def track_ids(self) -> set[str]:
        """Return unique track IDs in this album."""
        track_ids = set()
        for track in self.tracks:
            track_ids.add(track.track_id)
        return track_ids

    def duration_seconds(self) -> int:
        """Return the total duration of the album in seconds."""
        return sum(track.duration_seconds for track in self.tracks)
