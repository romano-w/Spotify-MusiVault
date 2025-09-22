import os
from importlib import reload

import pytest


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setenv('SPOTIFY_CLIENT_ID', 'dummy')
    monkeypatch.setenv('SPOTIFY_CLIENT_SECRET', 'dummy')
    monkeypatch.setenv('APP_SECRET_KEY', 'testing-secret')
    import app.app as app_module
    reload(app_module)
    app_module.app.config['TESTING'] = True
    with app_module.app.test_client() as client:
        yield client


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
