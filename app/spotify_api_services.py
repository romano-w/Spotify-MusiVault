import spotipy

def with_pagination(func):
    """
    A decorator that enables pagination for Spotify API requests.

    Parameters:
    - func (function): The function to be decorated.

    Returns:
    - wrapper (function): The decorated function.
    """
    def wrapper(sp, *args, **kwargs):
        items = []
        results = func(sp, *args, **kwargs)
        while results:
            items.extend(results['items'])
            results = sp.next(results) if results['next'] else None
        return items
    return wrapper

def get_user(sp):
    """
    Retrieves the current user from the Spotify API.

    Parameters:
    sp (Spotify): An instance of the Spotify class.

    Returns:
    dict: A dictionary containing the user's information.
    """
    return sp.current_user()

@with_pagination
def get_user_playlists(sp):
    return sp.current_user_playlists()

def get_playlist(sp, playlist_id):
    """
    Retrieves a playlist from Spotify.

    Parameters:
    sp (object): The Spotify object used for authentication and API calls.
    playlist_id (str): The ID of the playlist to retrieve.

    Returns:
    dict: A dictionary representing the playlist.
    """
    return sp.playlist(playlist_id)

@with_pagination
def get_playlist_items(sp, playlist_id):
    """
    Retrieves the items in a Spotify playlist.

    Args:
        sp (object): The Spotify API object.
        playlist_id (str): The ID of the playlist.

    Returns:
        dict: A dictionary containing the playlist items.
    """
    return sp.playlist_items(playlist_id)

def get_playlist_cover_image(sp, playlist_id):
    """
    Retrieves the cover image of a Spotify playlist.

    Args:
        sp (object): The Spotify object used for making API requests.
        playlist_id (str): The ID of the playlist.

    Returns:
        str: The URL of the playlist's cover image.
    """
    return sp.playlist_cover_image(playlist_id)

def get_track(sp, track_id):
    """
    Retrieves information about a track from Spotify.

    Parameters:
    sp (Spotify object): The Spotify object used for making API requests.
    track_id (str): The ID of the track to retrieve.

    Returns:
    dict: A dictionary containing information about the track.
    """
    return sp.track(track_id)

def get_several_tracks(sp, track_ids):
    """
    Retrieves several tracks from Spotify API based on their track IDs.

    Parameters:
    sp (SpotifyClient): An instance of the SpotifyClient class.
    track_ids (list): A list of track IDs.

    Returns:
    dict: A dictionary containing information about the retrieved tracks.
    """
    return sp.tracks(track_ids)

@with_pagination
def get_saved_tracks(sp):
    """
    Retrieves the saved tracks of the current user from Spotify.

    Args:
        sp (object): The Spotify object used for making API requests.

    Returns:
        dict: A dictionary containing information about the saved tracks.
    """
    return sp.current_user_saved_tracks()

def get_several_audio_features(sp, track_ids):
    return sp.audio_features(track_ids)

def get_track_audio_features(sp, track_id):
    """
    Retrieves the audio features of a track from Spotify.

    Parameters:
    - sp (Spotify object): The Spotify object used for making API requests.
    - track_id (str): The ID of the track.

    Returns:
    - list: A list containing the audio features of the track.
    """
    return sp.audio_features([track_id])

def get_track_audio_analysis(sp, track_id):
    """
    Retrieves the audio analysis for a given track from the Spotify API.

    Args:
        sp (spotipy.Spotify): An instance of the Spotipy client.
        track_id (str): The ID of the track.

    Returns:
        dict: The audio analysis data for the track.
    """
    return sp.audio_analysis(track_id)

def get_user_top_items(sp, type='tracks'):
    """
    Get the current user's top tracks or top artists.

    Parameters:
    - sp: Spotify client object
    - type: Type of items to retrieve ('tracks' or 'artists')

    Returns:
    - List of top tracks or top artists
    """
    return sp.current_user_top_tracks() if type == 'tracks' else sp.current_user_top_artists()

@with_pagination
def get_followed_artists(sp):
    """
    Retrieves the list of artists that the current user is following on Spotify.

    Args:
        sp (object): The Spotify API object.

    Returns:
        object: The list of followed artists.
    """
    return sp.current_user_followed_artists()
