def build_spotify_payloads():
    user = {
        'id': 'user-123',
        'display_name': 'Test User',
        'email': 'user@example.com',
        'country': 'US',
        'followers': {'total': 42},
        'external_urls': {'spotify': 'https://spotify.com/user-123'},
        'href': 'https://api.spotify.com/v1/users/user-123',
        'uri': 'spotify:user:user-123',
        'product': 'premium',
    }

    artist_one = {
        'id': 'artist-1',
        'name': 'Artist One',
        'genres': ['alt-rock'],
        'followers': {'total': 1_000},
        'images': [{'url': 'https://images/artist1.jpg'}],
        'external_urls': {'spotify': 'https://spotify.com/artist-1'},
        'href': 'https://api.spotify.com/v1/artists/artist-1',
        'uri': 'spotify:artist:artist-1',
        'popularity': 50,
    }

    artist_two = {
        'id': 'artist-2',
        'name': 'Artist Two',
        'genres': ['pop'],
        'followers': {'total': 2_000},
        'images': [{'url': 'https://images/artist2.jpg'}],
        'external_urls': {'spotify': 'https://spotify.com/artist-2'},
        'href': 'https://api.spotify.com/v1/artists/artist-2',
        'uri': 'spotify:artist:artist-2',
        'popularity': 75,
    }

    album_one = {
        'id': 'album-1',
        'name': 'Album One',
        'album_type': 'album',
        'total_tracks': 10,
        'release_date': '2024-01-01',
        'release_date_precision': 'day',
        'available_markets': ['US', 'GB'],
        'external_urls': {'spotify': 'https://spotify.com/album-1'},
        'href': 'https://api.spotify.com/v1/albums/album-1',
        'uri': 'spotify:album:album-1',
        'images': [{'url': 'https://images/album1.jpg'}],
        'label': 'Indie Label',
        'popularity': 60,
        'artists': [artist_one],
    }

    album_two = {
        'id': 'album-2',
        'name': 'Album Two',
        'album_type': 'single',
        'total_tracks': 1,
        'release_date': '2023-05-05',
        'release_date_precision': 'day',
        'available_markets': ['US'],
        'external_urls': {'spotify': 'https://spotify.com/album-2'},
        'href': 'https://api.spotify.com/v1/albums/album-2',
        'uri': 'spotify:album:album-2',
        'images': [{'url': 'https://images/album2.jpg'}],
        'label': 'Major Label',
        'popularity': 80,
        'artists': [artist_two],
    }

    track_one = {
        'id': 'track-1',
        'name': 'Track One',
        'duration_ms': 210000,
        'explicit': False,
        'popularity': 55,
        'preview_url': 'https://preview/track1.mp3',
        'track_number': 1,
        'disc_number': 1,
        'is_local': False,
        'available_markets': ['US', 'GB'],
        'external_urls': {'spotify': 'https://spotify.com/track-1'},
        'href': 'https://api.spotify.com/v1/tracks/track-1',
        'uri': 'spotify:track:track-1',
        'external_ids': {'isrc': 'US1234567890'},
        'album': album_one,
        'artists': [artist_one],
    }

    track_two = {
        'id': 'track-2',
        'name': 'Track Two',
        'duration_ms': 180000,
        'explicit': True,
        'popularity': 65,
        'preview_url': 'https://preview/track2.mp3',
        'track_number': 1,
        'disc_number': 1,
        'is_local': False,
        'available_markets': ['US'],
        'external_urls': {'spotify': 'https://spotify.com/track-2'},
        'href': 'https://api.spotify.com/v1/tracks/track-2',
        'uri': 'spotify:track:track-2',
        'external_ids': {'isrc': 'US0987654321'},
        'album': album_two,
        'artists': [artist_two],
    }

    playlist = {
        'id': 'playlist-1',
        'name': 'Playlist One',
        'description': 'A great playlist',
        'public': True,
        'collaborative': False,
        'followers': {'total': 10},
        'snapshot_id': 'snapshot-xyz',
        'external_urls': {'spotify': 'https://spotify.com/playlist-1'},
        'href': 'https://api.spotify.com/v1/playlists/playlist-1',
        'uri': 'spotify:playlist:playlist-1',
        'images': [{'url': 'https://images/playlist.jpg'}],
        'primary_color': None,
    }

    playlist_items = [{'track': track_one}]
    saved_tracks = [{'track': track_one, 'added_at': '2024-01-15T12:00:00Z'}]
    top_tracks = {'items': [track_two], 'time_range': 'short_term'}
    top_artists = {'items': [artist_one, artist_two], 'time_range': 'short_term'}

    playlists_payload = [{'playlist': playlist, 'items': playlist_items}]

    return user, playlists_payload, saved_tracks, top_tracks, top_artists


def test_store_user_snapshot_persists_entities(app_environment):
    _, app_module, data_access_module = app_environment
    SpotifyDataAccess = data_access_module.SpotifyDataAccess

    user, playlists, saved_tracks, top_tracks, top_artists = build_spotify_payloads()
    user_id = SpotifyDataAccess.store_user_snapshot(
        user, playlists=playlists, saved_tracks=saved_tracks, top_tracks=top_tracks, top_artists=top_artists
    )

    assert user_id == user['id']

    stored_user = SpotifyDataAccess.get_user(user_id)
    assert stored_user['display_name'] == 'Test User'
    assert stored_user['followers_total'] == 42

    playlists_data = SpotifyDataAccess.get_user_playlists(user_id)
    assert len(playlists_data) == 1
    playlist_data = playlists_data[0]
    assert playlist_data['name'] == 'Playlist One'
    assert playlist_data['tracks'][0]['artists'][0]['genres'] == ['alt-rock']
    assert playlist_data['tracks'][0]['album']['available_markets'] == ['US', 'GB']

    saved = SpotifyDataAccess.get_saved_tracks(user_id)
    assert len(saved) == 1
    saved_entry = saved[0]
    assert saved_entry['track']['available_markets'] == ['US', 'GB']
    assert saved_entry['added_at'].startswith('2024-01-15')

    top_tracks_data = SpotifyDataAccess.get_user_top_tracks(user_id)
    assert [entry['track']['id'] for entry in top_tracks_data] == ['track-2']
    assert top_tracks_data[0]['track']['available_markets'] == ['US']

    top_artists_data = SpotifyDataAccess.get_user_top_artists(user_id)
    assert [entry['artist']['id'] for entry in top_artists_data] == ['artist-1', 'artist-2']
    assert top_artists_data[0]['artist']['genres'] == ['alt-rock']


def test_sync_service_populates_routes(monkeypatch, app_environment):
    client, app_module, data_access_module = app_environment
    SpotifyDataAccess = data_access_module.SpotifyDataAccess

    user, playlists, saved_tracks, top_tracks, top_artists = build_spotify_payloads()

    playlist_map = {payload['playlist']['id']: payload['items'] for payload in playlists}

    monkeypatch.setattr(app_module, 'get_user', lambda sp: user)
    monkeypatch.setattr(app_module, 'get_user_playlists', lambda sp: [payload['playlist'] for payload in playlists])
    monkeypatch.setattr(
        app_module, 'get_playlist_items', lambda sp, playlist_id: playlist_map.get(playlist_id, [])
    )
    monkeypatch.setattr(app_module, 'get_saved_tracks', lambda sp: saved_tracks)
    monkeypatch.setattr(
        app_module,
        'get_user_top_items',
        lambda sp, item_type: top_tracks if item_type == 'tracks' else top_artists,
    )

    user_id = app_module.sync_spotify_data(None)
    assert user_id == user['id']

    with client.session_transaction() as session:
        session['current_user_id'] = user_id

    response = client.get('/user')
    assert response.status_code == 200
    assert response.get_json()['user']['display_name'] == 'Test User'

    playlists_response = client.get('/user/playlists')
    assert playlists_response.status_code == 200
    playlists_payload = playlists_response.get_json()['playlists']
    assert playlists_payload[0]['tracks'][0]['artists'][0]['genres'] == ['alt-rock']

    saved_response = client.get('/user/saved_tracks')
    assert saved_response.status_code == 200
    assert saved_response.get_json()['saved_tracks'][0]['track']['available_markets'] == ['US', 'GB']

    top_tracks_response = client.get('/user/top/tracks')
    assert top_tracks_response.status_code == 200
    assert top_tracks_response.get_json()['top_items'][0]['track']['id'] == 'track-2'

    playlist_id = playlists[0]['playlist']['id']
    playlist_detail = client.get(f'/playlist/{playlist_id}')
    assert playlist_detail.status_code == 200
    assert playlist_detail.get_json()['id'] == playlist_id
    assert playlist_detail.get_json()['tracks'][0]['album']['images'][0]['url'] == 'https://images/album1.jpg'
