import csv
from datetime import datetime
from pathlib import Path

CSV_HEADERS = ["timestamp", "video_id", "title", "url", "action", "playlist_id"]


def init_csv(path: Path) -> None:
    if not path.exists():
        with path.open("w", newline="", encoding="utf-8") as f:
            csv.DictWriter(f, fieldnames=CSV_HEADERS).writeheader()


def load_history(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


def append_history(video_id: str, title: str, url: str, action: str, playlist_id: str, path: Path) -> None:
    with path.open("a", newline="", encoding="utf-8") as f:
        csv.DictWriter(f, fieldnames=CSV_HEADERS).writerow({
            "timestamp":   datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "video_id":    video_id,
            "title":       title,
            "url":         url,
            "action":      action,
            "playlist_id": playlist_id,
        })


def was_previously_added(video_id: str, history: list[dict], playlist_id: str) -> bool:
    return any(
        r["video_id"] == video_id
        and r.get("playlist_id") == playlist_id
        and r.get("action") == "add"
        for r in history
    )
