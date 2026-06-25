import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch
from googleapiclient.errors import HttpError
from domain.models import AddResult, RemoveResult
from service.sync import process_add, process_remove


def make_http_error(status: int, reason: str = "") -> HttpError:
    resp = MagicMock()
    resp.status = status
    content = f'{{"error":{{"errors":[{{"reason":"{reason}"}}]}}}}'.encode()
    return HttpError(resp=resp, content=content)


@pytest.fixture
def yt():
    return MagicMock()


@pytest.fixture
def playlist():
    return {"id": "PL1", "title": "テストプレイリスト"}


@pytest.fixture
def add_file(tmp_path):
    f = tmp_path / "add.txt"
    f.write_text(
        "https://youtu.be/AAAAAAAAAAa | 動画A\n"
        "https://youtu.be/BBBBBBBBBBb | 動画B\n"
    )
    return f


@pytest.fixture
def remove_file(tmp_path):
    f = tmp_path / "remove.txt"
    f.write_text("https://youtu.be/AAAAAAAAAAa | 動画A\n")
    return f


class TestProcessAdd:
    def test_all_success(self, yt, playlist, add_file, tmp_path):
        yt.playlistItems().insert().execute.return_value = {}
        csv_path = tmp_path / "history.csv"
        with patch("service.sync.time.sleep"), \
             patch("service.sync.fetch_playlist_video_ids", return_value=set()):
            result = process_add(yt, playlist, [], add_file, csv_path)
        assert result.ok == 2
        assert result.confirmed_skip == 0
        assert result.already_in_playlist == []
        assert result.api_errors == []

    def test_empty_file(self, yt, playlist, tmp_path):
        f = tmp_path / "add.txt"
        f.write_text("")
        csv_path = tmp_path / "history.csv"
        result = process_add(yt, playlist, [], f, csv_path)
        assert result.ok == 0

    def test_file_not_found(self, yt, playlist, tmp_path):
        csv_path = tmp_path / "history.csv"
        result = process_add(yt, playlist, [], tmp_path / "add.txt", csv_path)
        assert result.ok == 0

    def test_existing_in_playlist_auto_skipped(self, yt, playlist, add_file, tmp_path):
        # ① プレイリスト既存 → 自動スキップ（確認なし）
        csv_path = tmp_path / "history.csv"
        with patch("service.sync.time.sleep"), \
             patch("service.sync.fetch_playlist_video_ids",
                   return_value={"AAAAAAAAAAa", "BBBBBBBBBBb"}):
            result = process_add(yt, playlist, [], add_file, csv_path)
        assert result.ok == 0
        assert len(result.already_in_playlist) == 2
        assert result.confirmed_skip == 0
        yt.playlistItems().insert.assert_not_called()

    def test_csv_existing_user_confirms(self, yt, playlist, add_file, tmp_path):
        # ① プレイリスト既存なし ② CSV既存 → ユーザーが Yes → 追加される
        history = [{"video_id": "AAAAAAAAAAa", "playlist_id": "PL1", "action": "add"}]
        yt.playlistItems().insert().execute.return_value = {}
        csv_path = tmp_path / "history.csv"
        with patch("service.sync.time.sleep"), \
             patch("service.sync.fetch_playlist_video_ids", return_value=set()), \
             patch("service.sync.questionary.confirm") as mock_q:
            mock_q.return_value.ask.return_value = True
            result = process_add(yt, playlist, history, add_file, csv_path)
        assert result.ok == 2
        assert result.confirmed_skip == 0

    def test_csv_existing_user_declines(self, yt, playlist, add_file, tmp_path):
        # ① プレイリスト既存なし ② CSV既存 → ユーザーが No → スキップ
        history = [{"video_id": "AAAAAAAAAAa", "playlist_id": "PL1", "action": "add"}]
        yt.playlistItems().insert().execute.return_value = {}
        csv_path = tmp_path / "history.csv"
        with patch("service.sync.time.sleep"), \
             patch("service.sync.fetch_playlist_video_ids", return_value=set()), \
             patch("service.sync.questionary.confirm") as mock_q:
            mock_q.return_value.ask.return_value = False
            result = process_add(yt, playlist, history, add_file, csv_path)
        assert result.confirmed_skip == 1
        assert result.ok == 1

    def test_409_fallback_collected(self, yt, playlist, add_file, tmp_path):
        # 事前チェックをすり抜けて409（競合フォールバック）
        yt.playlistItems().insert().execute.side_effect = make_http_error(409)
        csv_path = tmp_path / "history.csv"
        with patch("service.sync.time.sleep"), \
             patch("service.sync.fetch_playlist_video_ids", return_value=set()):
            result = process_add(yt, playlist, [], add_file, csv_path)
        assert result.ok == 0
        assert len(result.already_in_playlist) == 2

    def test_api_error_collected(self, yt, playlist, add_file, tmp_path):
        yt.playlistItems().insert().execute.side_effect = make_http_error(500)
        csv_path = tmp_path / "history.csv"
        with patch("service.sync.time.sleep"), \
             patch("service.sync.fetch_playlist_video_ids", return_value=set()):
            result = process_add(yt, playlist, [], add_file, csv_path)
        assert result.ok == 0
        assert len(result.api_errors) == 2


class TestProcessRemove:
    def test_all_success(self, yt, playlist, remove_file, tmp_path):
        yt.playlistItems().list().execute.return_value = {"items": [{"id": "item_001"}]}
        yt.playlistItems().delete().execute.return_value = {}
        csv_path = tmp_path / "history.csv"
        with patch("service.sync.time.sleep"):
            result = process_remove(yt, playlist, remove_file, csv_path)
        assert result.ok == 1
        assert result.not_found == []
        assert result.api_errors == []

    def test_empty_file(self, yt, playlist, tmp_path):
        f = tmp_path / "remove.txt"
        f.write_text("")
        csv_path = tmp_path / "history.csv"
        result = process_remove(yt, playlist, f, csv_path)
        assert result.ok == 0

    def test_file_not_found(self, yt, playlist, tmp_path):
        csv_path = tmp_path / "history.csv"
        result = process_remove(yt, playlist, tmp_path / "remove.txt", csv_path)
        assert result.ok == 0

    def test_not_in_playlist_collected(self, yt, playlist, remove_file, tmp_path):
        yt.playlistItems().list().execute.return_value = {"items": []}
        csv_path = tmp_path / "history.csv"
        with patch("service.sync.time.sleep"):
            result = process_remove(yt, playlist, remove_file, csv_path)
        assert result.ok == 0
        assert len(result.not_found) == 1

    def test_api_error_collected(self, yt, playlist, remove_file, tmp_path):
        yt.playlistItems().list().execute.side_effect = make_http_error(500)
        csv_path = tmp_path / "history.csv"
        with patch("service.sync.time.sleep"):
            result = process_remove(yt, playlist, remove_file, csv_path)
        assert len(result.api_errors) == 1
