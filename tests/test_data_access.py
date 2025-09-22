from app.data_access import SpotifyDataAccess


def test_create_or_update_user_persists_and_updates(db_session_factory):
    user_payload = {
        "id": "user-abc",
        "display_name": "Original",
        "email": "original@example.com",
        "country": "US",
        "followers": {"total": 5},
        "external_urls": {"spotify": "https://spotify/user-abc"},
        "href": "https://api.spotify.com/user-abc",
        "uri": "spotify:user:user-abc",
        "product": "premium",
    }

    created = SpotifyDataAccess.create_or_update_user(user_payload)
    assert created["display_name"] == "Original"
    assert created["followers_total"] == 5

    updated_payload = dict(user_payload)
    updated_payload["display_name"] = "Updated"
    updated_payload["followers"] = {"total": 10}

    updated = SpotifyDataAccess.create_or_update_user(updated_payload)
    assert updated["display_name"] == "Updated"
    assert updated["followers_total"] == 10


def test_database_stats_reflect_insertions(db_session_factory):
    SpotifyDataAccess.create_or_update_user({
        "id": "stats-user",
        "display_name": "Stats User",
    })
    SpotifyDataAccess.create_or_update_artist({
        "id": "artist-stats",
        "name": "Stats Artist",
    })

    stats = SpotifyDataAccess.get_database_stats()
    assert stats["users"] == 1
    assert stats["artists"] == 1
