import pytest

@pytest.fixture
def client(app_environment):
    client, _, _ = app_environment
    return client


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
