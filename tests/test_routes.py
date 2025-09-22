import time

from app.models import User


def test_index_redirects_to_login(client):
    response = client.get('/')
    assert response.status_code == 302
    assert '/login' in response.headers['Location']


def test_login_redirects(client):
    response = client.get('/login')
    assert response.status_code == 302
    assert 'accounts.spotify.com' in response.headers['Location']


def test_protected_route_redirects_without_token(client):
    response = client.get('/user')
    assert response.status_code == 302
    assert '/login' in response.headers['Location']


def test_db_test_reports_counts(client, db_session_factory):
    with db_session_factory() as session:
        session.add(User(id='route-user', display_name='Route User'))

    response = client.get('/db-test')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'success'
    assert data['user_count'] == 1


def test_db_stats_returns_expected_totals(client, db_session_factory):
    with db_session_factory() as session:
        session.add(User(id='stats-user', display_name='Stats User'))

    response = client.get('/db-stats')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'success'
    assert data['stats']['users'] == 1


def test_user_route_uses_spotify_session(client, fake_spotify_factory, monkeypatch):
    fake_spotify = fake_spotify_factory(current_user={'id': 'tester'})
    monkeypatch.setattr('spotipy.Spotify', lambda *args, **kwargs: fake_spotify)

    with client.session_transaction() as session:
        session['spotify_token'] = {
            'access_token': 'token',
            'expires_at': int(time.time()) + 3600,
        }

    response = client.get('/user')
    assert response.status_code == 200
    assert response.get_json() == {'id': 'tester'}
