import json
import pytest
from datetime import datetime, timezone, timedelta
from freezegun import freeze_time
from pathlib import Path
from repository.cache import load_playlist_cache, save_playlist_cache, add_to_cache, remove_from_cache

PLAYLIST_ID = "PL_TEST_001"


def write_cache(cache_dir: Path, playlist_id: str, video_ids: list[str], fetched_at: str) -> None:
    path = cache_dir / f"playlist_cache_{playlist_id}.json"
    path.write_text(json.dumps({"fetched_at": fetched_at, "video_ids": video_ids}))


class TestLoadPlaylistCache:
    def test_returns_none_when_no_cache_file(self, tmp_path):
        assert load_playlist_cache(PLAYLIST_ID, tmp_path) is None

    def test_returns_video_ids_when_cache_is_fresh(self, tmp_path):
        fetched_at = (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat()
        write_cache(tmp_path, PLAYLIST_ID, ["abc", "def"], fetched_at)
        result = load_playlist_cache(PLAYLIST_ID, tmp_path)
        assert result == {"abc", "def"}

    def test_returns_none_when_cache_is_expired(self, tmp_path):
        fetched_at = (datetime.now(timezone.utc) - timedelta(hours=24)).isoformat()
        write_cache(tmp_path, PLAYLIST_ID, ["abc"], fetched_at)
        assert load_playlist_cache(PLAYLIST_ID, tmp_path) is None

    def test_returns_none_when_cache_is_exactly_at_ttl(self, tmp_path):
        # TTL=23h のちょうど境界は無効
        fetched_at = (datetime.now(timezone.utc) - timedelta(hours=23)).isoformat()
        write_cache(tmp_path, PLAYLIST_ID, ["abc"], fetched_at)
        assert load_playlist_cache(PLAYLIST_ID, tmp_path) is None


class TestSavePlaylistCache:
    def test_creates_cache_file_with_video_ids(self, tmp_path):
        save_playlist_cache(PLAYLIST_ID, {"abc", "def"}, tmp_path)
        path = tmp_path / f"playlist_cache_{PLAYLIST_ID}.json"
        assert path.exists()
        data = json.loads(path.read_text())
        assert set(data["video_ids"]) == {"abc", "def"}

    @freeze_time("2026-06-26T10:00:00+00:00")
    def test_sets_fetched_at_to_current_utc_time(self, tmp_path):
        save_playlist_cache(PLAYLIST_ID, {"abc"}, tmp_path)
        path = tmp_path / f"playlist_cache_{PLAYLIST_ID}.json"
        data = json.loads(path.read_text())
        fetched_at = datetime.fromisoformat(data["fetched_at"])
        assert fetched_at.replace(tzinfo=timezone.utc) == datetime(2026, 6, 26, 10, 0, 0, tzinfo=timezone.utc)

    def test_overwrites_existing_cache(self, tmp_path):
        save_playlist_cache(PLAYLIST_ID, {"old"}, tmp_path)
        save_playlist_cache(PLAYLIST_ID, {"new"}, tmp_path)
        path = tmp_path / f"playlist_cache_{PLAYLIST_ID}.json"
        data = json.loads(path.read_text())
        assert set(data["video_ids"]) == {"new"}


class TestAddToCache:
    def test_adds_video_id_to_existing_cache(self, tmp_path):
        write_cache(tmp_path, PLAYLIST_ID, ["abc"], datetime.now(timezone.utc).isoformat())
        add_to_cache(PLAYLIST_ID, "xyz", tmp_path)
        path = tmp_path / f"playlist_cache_{PLAYLIST_ID}.json"
        data = json.loads(path.read_text())
        assert set(data["video_ids"]) == {"abc", "xyz"}

    def test_does_nothing_when_no_cache_file(self, tmp_path):
        add_to_cache(PLAYLIST_ID, "xyz", tmp_path)
        assert not (tmp_path / f"playlist_cache_{PLAYLIST_ID}.json").exists()

    def test_does_not_duplicate_existing_video_id(self, tmp_path):
        write_cache(tmp_path, PLAYLIST_ID, ["abc"], datetime.now(timezone.utc).isoformat())
        add_to_cache(PLAYLIST_ID, "abc", tmp_path)
        path = tmp_path / f"playlist_cache_{PLAYLIST_ID}.json"
        data = json.loads(path.read_text())
        assert data["video_ids"].count("abc") == 1


class TestRemoveFromCache:
    def test_removes_video_id_from_existing_cache(self, tmp_path):
        write_cache(tmp_path, PLAYLIST_ID, ["abc", "xyz"], datetime.now(timezone.utc).isoformat())
        remove_from_cache(PLAYLIST_ID, "abc", tmp_path)
        path = tmp_path / f"playlist_cache_{PLAYLIST_ID}.json"
        data = json.loads(path.read_text())
        assert set(data["video_ids"]) == {"xyz"}

    def test_does_nothing_when_no_cache_file(self, tmp_path):
        remove_from_cache(PLAYLIST_ID, "abc", tmp_path)
        assert not (tmp_path / f"playlist_cache_{PLAYLIST_ID}.json").exists()

    def test_does_nothing_when_video_id_not_in_cache(self, tmp_path):
        write_cache(tmp_path, PLAYLIST_ID, ["abc"], datetime.now(timezone.utc).isoformat())
        remove_from_cache(PLAYLIST_ID, "xyz", tmp_path)
        path = tmp_path / f"playlist_cache_{PLAYLIST_ID}.json"
        data = json.loads(path.read_text())
        assert set(data["video_ids"]) == {"abc"}
