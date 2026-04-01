from __future__ import annotations

from datetime import datetime, timedelta
from typing import TYPE_CHECKING

#these are used in the actual code
from streaming.playlists import CollaborativePlaylist, Playlist
from streaming.tracks import Song, Track
from streaming.users import FamilyMember, PremiumUser, User

if TYPE_CHECKING:
  #only used for type hints, not actual code execution, so we can avoid circular imports (or unnecessarily imported)
  from streaming.albums import Album
  from streaming.artists import Artist
  from streaming.sessions import ListeningSession


class StreamingPlatform:
  """Central registry and query surface for all streaming entities."""

  def __init__(self, name: str) -> None:
    self.name = name
    self._catalogue = {}
    self._users = {}
    self._artists = {}
    self._albums = {}
    self._playlists = {}
    self._sessions = []

  def add_track(self, track: Track) -> None:
    self._catalogue[track.track_id] = track

  def add_user(self, user: User) -> None:
    self._users[user.user_id] = user

  def add_artist(self, artist: Artist) -> None:
    self._artists[artist.artist_id] = artist

  def add_album(self, album: Album) -> None:
    self._albums[album.album_id] = album

  def add_playlist(self, playlist: Playlist) -> None:
    self._playlists[playlist.playlist_id] = playlist

  def record_session(self, session: ListeningSession) -> None:
    self._sessions.append(session)
    session.user.add_session(session)

  def get_track(self, track_id: str) -> Track | None:
    return self._catalogue.get(track_id)

  def get_user(self, user_id: str) -> User | None:
    return self._users.get(user_id)

  def get_artist(self, artist_id: str) -> Artist | None:
    return self._artists.get(artist_id)

  def get_album(self, album_id: str) -> Album | None:
    return self._albums.get(album_id)

  def all_users(self) -> list[User]:
    return list(self._users.values())

  def all_tracks(self) -> list[Track]:
    return list(self._catalogue.values())

  def total_listening_time_minutes(self, start: datetime, end: datetime) -> float:
    total_seconds = 0
    for session in self._sessions:
      if start <= session.timestamp <= end:
        total_seconds += session.duration_listened_seconds
    return total_seconds / 60

  def avg_unique_tracks_per_premium_user(self, days: int = 30) -> float:
    premium_users = []
    
    # get premium users
    for user in self._users.values():
      if type(user) is PremiumUser:
        premium_users.append(user)
    if not premium_users:
      return 0.0

    now = datetime.now()
    start_date = now - timedelta(days=days) # from when
    unique_tracks_by_user = {}
    
    # init unique utracks for each
    for user in premium_users:
      unique_tracks_by_user[user.user_id] = []

    # for every session - check if user premium, add track if not already added
    for session in self._sessions:
      if session.user.user_id not in unique_tracks_by_user: #user not premium
        continue
      
      if start_date <= session.timestamp <= now: 
        track_ids = unique_tracks_by_user[session.user.user_id]

        # add track to the users track id's
        if session.track.track_id not in track_ids:
          track_ids.append(session.track.track_id)

  # count
    total_unique = 0
    for track_ids in unique_tracks_by_user.values():
      total_unique += len(track_ids)
    return total_unique / len(premium_users)

  def track_with_most_distinct_listeners(self) -> Track | None:
    # no sessions no top track
    if not self._sessions:
      return None

    listeners_by_track = {}

    # build a map: track_id -> unique user ids who listened
    for session in self._sessions:
      track_id = session.track.track_id
      
      if track_id not in self._catalogue:
        continue
      
      if track_id not in listeners_by_track:
        listeners_by_track[track_id] = []
        
      user_ids = listeners_by_track[track_id]
      if session.user.user_id not in user_ids:
        user_ids.append(session.user.user_id)

    #fallback
    if not listeners_by_track:
      return None

    # find the track with the biggest listener count
    best_track = None
    best_count = -1
    
    for track in self._catalogue.values():
      count = len(listeners_by_track.get(track.track_id, [])) #number of user id's for track
      if count > best_count:
        best_track = track
        best_count = count
    return best_track

  def avg_session_duration_by_user_type(self) -> list[tuple[str, float]]:
    durations_by_type = {}

    # ensure every registered user type exists in output, even with no sessions
    for user in self._users.values():
      user_type = type(user).__name__
      if user_type not in durations_by_type:
        durations_by_type[user_type] = []

    # collect session durations grouped by concrete user type
    for session in self._sessions:
      type_name = type(session.user).__name__
      if type_name not in durations_by_type:
        durations_by_type[type_name] = []
      durations_by_type[type_name].append(session.duration_listened_seconds)

    # compute per-type averages
    averages = []
    for type_name, durations in durations_by_type.items():
      if durations:
        averages.append((type_name, sum(durations) / len(durations)))
      else:
        averages.append((type_name, 0.0))

    # sort longest average duration first
    return sorted(averages, key=lambda item: (-item[1], item[0]))

  def total_listening_time_underage_sub_users_minutes(self, age_threshold: int = 18) -> float:
    total_seconds = 0

    # only include family members under the threshold
    for session in self._sessions:
      if type(session.user) is FamilyMember and session.user.age < age_threshold:
        total_seconds += session.duration_listened_seconds

    # convert seconds to minutes
    return total_seconds / 60

  def top_artists_by_listening_time(self, n: int = 5) -> list[tuple[Artist, float]]:
    seconds_by_artist = {}
    artists_by_id = {}

    # count listening seconds per artist, songs only
    for session in self._sessions:
      if type(session.track) is not Song:
        continue
      artist = session.track.artist
      artists_by_id[artist.artist_id] = artist
      
      
      seconds_by_artist[artist.artist_id] = (
        seconds_by_artist.get(artist.artist_id, 0.0) + session.duration_listened_seconds
      )

    # rank artists by total listening time desc
    ranked_artist_ids = sorted(
      seconds_by_artist.keys(),
      key=lambda artist_id: (-seconds_by_artist[artist_id], artist_id),
    )

    # return top n as (artist, minutes)
    top_ids = ranked_artist_ids[:n]
    top_artists = []
    for artist_id in top_ids:
      top_artists.append((artists_by_id[artist_id], seconds_by_artist[artist_id] / 60))
      
    return top_artists

  def user_top_genre(self, user_id: str) -> tuple[str, float] | None:
    # user must exist
    user = self.get_user(user_id)
    if user is None:
      return None

    genre_seconds = {}
    total_seconds = 0

    # totaol listening seconds by genre for this user
    for session in self._sessions:
      if session.user.user_id != user.user_id:
        continue
      
      genre_seconds[session.track.genre] = (
        genre_seconds.get(session.track.genre, 0) + session.duration_listened_seconds
      )
      total_seconds += session.duration_listened_seconds

    # no listening history
    if total_seconds == 0:
      return None

    # === the top genre - genre:seconds key-value pairs sorted by seconds, take just the genre (item 0)
    top_genre = max(genre_seconds.items(), key=lambda item: item[1])[0]
    percentage = (genre_seconds[top_genre] / total_seconds) * 100
    return top_genre, percentage

  def collaborative_playlists_with_many_artists(self, threshold: int = 3) -> list[CollaborativePlaylist]:
    matching_playlists = []

    # inspect only collaborative playlists
    for playlist in self._playlists.values():
      if type(playlist) is not CollaborativePlaylist:
        continue

      # collect distinct artist ids from song tracks in this playlist
      artist_ids = []
      for track in playlist.tracks:
        
        if type(track) is Song:
          artist_id = track.artist.artist_id
          
          if artist_id not in artist_ids:
            artist_ids.append(artist_id)

      # keep playlists that exceed threshold
      if len(artist_ids) > threshold:
        matching_playlists.append(playlist)
        
    return matching_playlists

  def avg_tracks_per_playlist_type(self) -> dict[str, float]:
    standard_playlists = []
    collaborative_playlists = []

    # split playlists by type (normal, collaborative)
    for playlist in self._playlists.values():
      if type(playlist) is Playlist:
        standard_playlists.append(playlist)
        
      elif type(playlist) is CollaborativePlaylist:
        collaborative_playlists.append(playlist)

    # average track count for standard playlists
    standard_avg = 0.0
    if standard_playlists:
      standard_total = 0
      
      for playlist in standard_playlists:
        standard_total += len(playlist.tracks)
      standard_avg = standard_total / len(standard_playlists)

    # and for collaborative playlists
    collaborative_avg = 0.0
    if collaborative_playlists:
      collaborative_total = 0
      
      for playlist in collaborative_playlists:
        collaborative_total += len(playlist.tracks)
        
      collaborative_avg = collaborative_total / len(collaborative_playlists)

    return {
      "Playlist": standard_avg,
      "CollaborativePlaylist": collaborative_avg,
    }

  def users_who_completed_albums(self) -> list[tuple[User, list[str]]]:
    sessions_by_user = {}

    # map each user to unique track ids they have listened to
    for session in self._sessions:
      user_id = session.user.user_id
      
      if user_id not in sessions_by_user:
        sessions_by_user[user_id] = []
        
      listened_track_ids = sessions_by_user[user_id]
      
      if session.track.track_id not in listened_track_ids:
        listened_track_ids.append(session.track.track_id)

    completed_by_user = []

    # for each user, check which albums are fully completed
    for user in self._users.values():
      listened_track_ids = sessions_by_user.get(user.user_id, [])
      completed_albums = []

      for album in self._albums.values():
        album_track_ids = album.track_ids()
        if not album_track_ids:
          continue

        # user must have listened to every track on the album
        completed = True
        for album_track_id in album_track_ids:
          
          if album_track_id not in listened_track_ids:
            completed = False
            break
          
        if completed:
          completed_albums.append(album.title)

      # include only users with at least one completed album
      if completed_albums:
        completed_by_user.append((user, completed_albums))

    return completed_by_user
