import pytest
from unittest.mock import MagicMock
from repository.youtube import fetch_playlists


class TestFetchPlaylists:
    def test_returns_list_with_id_and_title(self):
        yt = MagicMock()
        yt.playlists().list().execute.return_value = {
            "items": [
                {"id": "PL1", "snippet": {"title": "AIプレイリスト"}},
                {"id": "PL2", "snippet": {"title": "学習リスト"}},
            ]
        }
        result = fetch_playlists(yt)
        assert result == [
            {"id": "PL1", "title": "AIプレイリスト"},
            {"id": "PL2", "title": "学習リスト"},
        ]

    def test_empty_playlists_returns_empty_list(self):
        yt = MagicMock()
        yt.playlists().list().execute.return_value = {"items": []}
        assert fetch_playlists(yt) == []

    def test_missing_items_key_returns_empty_list(self):
        yt = MagicMock()
        yt.playlists().list().execute.return_value = {}
        assert fetch_playlists(yt) == []
