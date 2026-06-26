import json
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path

_DEFAULT_TTL_HOURS = int(os.environ.get("CACHE_TTL_HOURS", "23"))


def _cache_path(cache_dir: Path, playlist_id: str) -> Path:
    return cache_dir / f"playlist_cache_{playlist_id}.json"


def load_playlist_cache(playlist_id: str, cache_dir: Path) -> set[str] | None:
    path = _cache_path(cache_dir, playlist_id)
    if not path.exists():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    fetched_at = datetime.fromisoformat(data["fetched_at"])
    if datetime.now(timezone.utc) - fetched_at >= timedelta(hours=_DEFAULT_TTL_HOURS):
        return None
    return set(data["video_ids"])


def save_playlist_cache(playlist_id: str, video_ids: set[str], cache_dir: Path) -> None:
    path = _cache_path(cache_dir, playlist_id)
    path.write_text(
        json.dumps({"fetched_at": datetime.now(timezone.utc).isoformat(), "video_ids": list(video_ids)}),
        encoding="utf-8",
    )


def add_to_cache(playlist_id: str, video_id: str, cache_dir: Path) -> None:
    path = _cache_path(cache_dir, playlist_id)
    if not path.exists():
        return
    data = json.loads(path.read_text(encoding="utf-8"))
    ids = set(data["video_ids"])
    ids.add(video_id)
    data["video_ids"] = list(ids)
    path.write_text(json.dumps(data), encoding="utf-8")


def remove_from_cache(playlist_id: str, video_id: str, cache_dir: Path) -> None:
    path = _cache_path(cache_dir, playlist_id)
    if not path.exists():
        return
    data = json.loads(path.read_text(encoding="utf-8"))
    ids = set(data["video_ids"])
    ids.discard(video_id)
    data["video_ids"] = list(ids)
    path.write_text(json.dumps(data), encoding="utf-8")
