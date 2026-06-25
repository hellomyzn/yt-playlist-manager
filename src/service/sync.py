import os
import time
from pathlib import Path

import questionary
from googleapiclient.errors import HttpError

from domain.models import AddResult, RemoveResult
from domain.parser import parse_input
from repository.history import append_history, was_previously_added
from repository.youtube import api_add_video, api_remove_video


def _interval() -> float:
    return float(os.environ.get("INTERVAL_SECONDS", "1.0"))


def process_add(youtube, playlist: dict, history: list[dict], add_file: Path, csv_path: Path) -> AddResult:
    result = AddResult()
    if not add_file.exists() or not add_file.read_text().strip():
        print("[INFO] add.txt なし/空 → スキップ")
        return result

    parsed = parse_input(add_file)
    for video_id, title, url in parsed.items:
        if was_previously_added(video_id, history, playlist["id"]):
            answer = questionary.confirm(
                f"「{title or video_id}」は過去に同プレイリストへ追加済みです。再追加しますか？"
            ).ask()
            if not answer:
                result.confirmed_skip += 1
                continue

        time.sleep(_interval())
        try:
            if api_add_video(youtube, playlist["id"], video_id):
                append_history(video_id, title, url, "add", playlist["id"], csv_path)
                history.append({"video_id": video_id, "playlist_id": playlist["id"], "action": "add"})
                print(f"[OK] 追加: {title or video_id}")
                result.ok += 1
            else:
                result.already_in_playlist.append((video_id, title))
        except HttpError as e:
            result.api_errors.append((video_id, title, str(e)))
            print(f"[ERROR] 追加失敗 {video_id}: {e}")

    return result


def process_remove(youtube, playlist: dict, remove_file: Path, csv_path: Path) -> RemoveResult:
    result = RemoveResult()
    if not remove_file.exists() or not remove_file.read_text().strip():
        print("[INFO] remove.txt なし/空 → スキップ")
        return result

    parsed = parse_input(remove_file)
    for video_id, title, url in parsed.items:
        time.sleep(_interval())
        try:
            if api_remove_video(youtube, playlist["id"], video_id):
                append_history(video_id, title, url, "remove", playlist["id"], csv_path)
                print(f"[OK] 削除: {title or video_id}")
                result.ok += 1
            else:
                result.not_found.append((video_id, title))
        except HttpError as e:
            result.api_errors.append((video_id, title, str(e)))
            print(f"[ERROR] 削除失敗 {video_id}: {e}")

    return result
