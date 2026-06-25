import pytest
from unittest.mock import MagicMock
from repository.youtube import fetch_playlists, fetch_playlist_video_ids


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


class TestFetchPlaylistVideoIds:
    def test_returns_set_of_video_ids(self):
        yt = MagicMock()
        yt.playlistItems().list().execute.return_value = {
            "items": [
                {"snippet": {"resourceId": {"videoId": "AAAAAAAAAAa"}}},
                {"snippet": {"resourceId": {"videoId": "BBBBBBBBBBb"}}},
            ]
        }
        result = fetch_playlist_video_ids(yt, "PL1")
        assert result == {"AAAAAAAAAAa", "BBBBBBBBBBb"}

    def test_empty_playlist_returns_empty_set(self):
        yt = MagicMock()
        yt.playlistItems().list().execute.return_value = {"items": []}
        assert fetch_playlist_video_ids(yt, "PL1") == set()

    def test_paginates_through_all_pages(self):
        yt = MagicMock()
        first_page = {
            "items": [{"snippet": {"resourceId": {"videoId": "AAAAAAAAAAa"}}}],
            "nextPageToken": "tok1",
        }
        second_page = {
            "items": [{"snippet": {"resourceId": {"videoId": "BBBBBBBBBBb"}}}],
        }
        yt.playlistItems().list().execute.side_effect = [first_page, second_page]
        result = fetch_playlist_video_ids(yt, "PL1")
        assert result == {"AAAAAAAAAAa", "BBBBBBBBBBb"}
