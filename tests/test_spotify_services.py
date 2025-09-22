from app import spotify_api_services as services


def test_get_user_playlists_handles_pagination(fake_spotify_factory):
    first_page = {
        "items": [{"id": "one"}],
        "next": "page2",
    }
    second_page = {
        "items": [{"id": "two"}],
        "next": None,
    }
    sp = fake_spotify_factory(current_user_playlists=first_page, page2=second_page)

    playlists = services.get_user_playlists(sp)

    assert [item["id"] for item in playlists] == ["one", "two"]
    assert "current_user_playlists" in sp.calls


def test_get_followed_artists_accumulates_pages(fake_spotify_factory):
    first_page = {
        "artists": {
            "items": [{"id": "artist-a"}],
            "next": "followed-page2",
        }
    }
    second_page = {
        "artists": {
            "items": [{"id": "artist-b"}],
            "next": None,
        }
    }
    sp = fake_spotify_factory(
        current_user_followed_artists=first_page,
        **{"followed-page2": second_page},
    )

    artists = services.get_followed_artists(sp)
    assert [artist["id"] for artist in artists] == ["artist-a", "artist-b"]
    assert "current_user_followed_artists" in sp.calls


def test_get_user_returns_payload(fake_spotify_factory):
    sp = fake_spotify_factory(current_user={"id": "tester"})
    assert services.get_user(sp) == {"id": "tester"}
