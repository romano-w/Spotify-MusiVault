from importlib import reload

import pytest


@pytest.fixture
def app_environment(monkeypatch, tmp_path):
    db_path = tmp_path / "test.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_path}")
    monkeypatch.setenv('SPOTIFY_CLIENT_ID', 'dummy')
    monkeypatch.setenv('SPOTIFY_CLIENT_SECRET', 'dummy')
    monkeypatch.setenv('APP_SECRET_KEY', 'testing-secret')

    import app.database as database_module
    import app.data_access as data_access_module
    import app.app as app_module

    database_module = reload(database_module)
    data_access_module = reload(data_access_module)
    app_module = reload(app_module)
    app_module.app.config['TESTING'] = True

    with app_module.app.test_client() as client:
        yield client, app_module, data_access_module
