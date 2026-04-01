from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from streaming.tracks import Track
    from streaming.users import User


class Playlist:
    """User-owned ordered collection of tracks."""

    def __init__(self, playlist_id: str, name: str, owner: User) -> None:
        self.playlist_id = playlist_id
        self.name = name
        self.owner = owner
        self.tracks = []

    def add_track(self, track: Track) -> None:
        if track not in self.tracks:
            self.tracks.append(track)

    def remove_track(self, track_id: str) -> None:
        self.tracks = [track for track in self.tracks if track.track_id != track_id]

    def total_duration_seconds(self) -> int:
        return sum(track.duration_seconds for track in self.tracks)


class CollaborativePlaylist(Playlist):
    """Playlist that can be edited by multiple contributors."""

    def __init__(self, playlist_id: str, name: str, owner: User) -> None:
        super().__init__(playlist_id, name, owner)
        self.contributors = [owner]

    def add_contributor(self, user: User) -> None:
        if user not in self.contributors:
            self.contributors.append(user)

    def remove_contributor(self, user: User) -> None:
        if user is self.owner:
            return
        self.contributors = [contributor for contributor in self.contributors if contributor is not user]
