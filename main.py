#!/usr/bin/env python3
import csv
import json
import os
import re
import sys
import time
from datetime import datetime
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import questionary
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# ── Constants ─────────────────────────────────────────────────────────────────

SCOPES       = ["https://www.googleapis.com/auth/youtube"]
HISTORY_CSV  = Path("playlist_history.csv")
ADD_FILE     = Path("input/add.txt")
REMOVE_FILE  = Path("input/remove.txt")
CONFIG_JSON  = Path("config.json")
CSV_HEADERS  = ["timestamp", "video_id", "title", "url", "action", "playlist_id"]
INTERVAL_SEC = float(os.environ.get("INTERVAL_SECONDS", "1.0"))
QUOTA_WAIT   = 60


# ── Auth ──────────────────────────────────────────────────────────────────────

def build_youtube_client():
    creds = None
    token_path = Path("token.json")

    if token_path.exists():
        creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("client_secret.json", SCOPES)
            auth_url, _ = flow.authorization_url(prompt="consent")
            print(f"\n以下のURLをブラウザで開いてください:\n\n  {auth_url}\n")
            code = input("認証コードを入力してください: ").strip()
            flow.fetch_token(code=code)
            creds = flow.credentials

        token_path.write_text(creds.to_json(), encoding="utf-8")
        print("[OK] token.json を保存しました。")

    return build("youtube", "v3", credentials=creds)


# ── Config ────────────────────────────────────────────────────────────────────

def load_config() -> dict:
    if CONFIG_JSON.exists():
        return json.loads(CONFIG_JSON.read_text(encoding="utf-8"))
    return {}


def save_config(config: dict) -> None:
    CONFIG_JSON.write_text(json.dumps(config, ensure_ascii=False, indent=2), encoding="utf-8")


# ── CSV ───────────────────────────────────────────────────────────────────────

def init_csv() -> None:
    if not HISTORY_CSV.exists():
        with HISTORY_CSV.open("w", newline="", encoding="utf-8") as f:
            csv.DictWriter(f, fieldnames=CSV_HEADERS).writeheader()


def load_history() -> list[dict]:
    with HISTORY_CSV.open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


def append_history(video_id: str, title: str, url: str, action: str, playlist_id: str) -> None:
    with HISTORY_CSV.open("a", newline="", encoding="utf-8") as f:
        csv.DictWriter(f, fieldnames=CSV_HEADERS).writerow({
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "video_id": video_id,
            "title": title,
            "url": url,
            "action": action,
            "playlist_id": playlist_id,
        })


def was_previously_added(video_id: str, history: list[dict], playlist_id: str) -> bool:
    return any(
        r["video_id"] == video_id
        and r.get("playlist_id") == playlist_id
        and r.get("action") == "add"
        for r in history
    )


# ── Input Parsing ─────────────────────────────────────────────────────────────

def extract_video_id(url: str) -> str | None:
    parsed = urlparse(url.strip())
    hostname = parsed.hostname or ""

    if hostname in ("www.youtube.com", "youtube.com", "m.youtube.com"):
        if parsed.path == "/watch":
            vid = parse_qs(parsed.query).get("v", [None])[0]
        elif parsed.path.startswith(("/shorts/", "/embed/", "/v/")):
            vid = parsed.path.split("/")[2]
        else:
            return None
    elif hostname == "youtu.be":
        vid = parsed.path.lstrip("/")
    else:
        return None

    return vid if vid and re.match(r"^[A-Za-z0-9_-]{11}$", vid) else None


def parse_input(path: Path) -> list[tuple[str, str, str]]:
    """Return deduplicated list of (video_id, title, url)."""
    seen: set[str] = set()
    results = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        parts = line.split("|", 1)
        url   = parts[0].strip()
        title = parts[1].strip() if len(parts) > 1 else ""
        vid   = extract_video_id(url)
        if not vid:
            print(f"[WARN] video_id を抽出できません: {line}")
            continue
        if vid in seen:
            print(f"[INFO] 重複スキップ: {vid}")
            continue
        seen.add(vid)
        results.append((vid, title, url))
    return results


# ── Playlist Selection ────────────────────────────────────────────────────────

def fetch_playlists(youtube) -> list[dict]:
    playlists = []
    req = youtube.playlists().list(part="snippet", mine=True, maxResults=50)
    while req:
        res = req.execute()
        for item in res.get("items", []):
            playlists.append({"id": item["id"], "title": item["snippet"]["title"]})
        req = youtube.playlists().list_next(req, res)
    return playlists


def select_playlist(playlists: list[dict], prompt: str, default_id: str | None) -> dict:
    choices = []
    default_choice = None
    for p in playlists:
        choice = questionary.Choice(title=f"{p['title']}  ({p['id']})", value=p)
        choices.append(choice)
        if p["id"] == default_id:
            default_choice = choice

    selected = questionary.select(prompt, choices=choices, default=default_choice).ask()
    if selected is None:
        sys.exit(0)
    return selected


def choose_playlists(youtube) -> tuple[dict, dict]:
    config   = load_config()
    playlists = fetch_playlists(youtube)

    if not playlists:
        print("[ERROR] プレイリストが見つかりません。")
        sys.exit(1)

    print()
    add_pl    = select_playlist(playlists, "追加先プレイリストを選択:", config.get("last_add_playlist_id"))
    remove_pl = select_playlist(playlists, "削除元プレイリストを選択:", config.get("last_remove_playlist_id"))

    config["last_add_playlist_id"]    = add_pl["id"]
    config["last_remove_playlist_id"] = remove_pl["id"]
    save_config(config)

    return add_pl, remove_pl


# ── YouTube API ───────────────────────────────────────────────────────────────

def api_call_with_retry(fn):
    while True:
        try:
            return fn()
        except HttpError as e:
            if e.resp.status == 403 and "quotaExceeded" in str(e):
                print(f"[WARN] Quota超過。{QUOTA_WAIT}秒後に再試行... (Ctrl+C で中断)")
                time.sleep(QUOTA_WAIT)
            else:
                raise


def api_add_video(youtube, playlist_id: str, video_id: str) -> bool:
    try:
        api_call_with_retry(lambda: youtube.playlistItems().insert(
            part="snippet",
            body={"snippet": {
                "playlistId": playlist_id,
                "resourceId": {"kind": "youtube#video", "videoId": video_id},
            }},
        ).execute())
        return True
    except HttpError as e:
        if e.resp.status == 409:
            print(f"[WARN] すでにプレイリストに存在します: {video_id}")
        else:
            print(f"[ERROR] 追加失敗 {video_id}: {e}")
        return False


def _get_playlist_item_id(youtube, playlist_id: str, video_id: str) -> str | None:
    try:
        res = api_call_with_retry(lambda: youtube.playlistItems().list(
            part="id", playlistId=playlist_id, videoId=video_id
        ).execute())
        items = res.get("items", [])
        return items[0]["id"] if items else None
    except HttpError as e:
        print(f"[ERROR] playlistItem取得失敗 {video_id}: {e}")
        return None


def api_remove_video(youtube, playlist_id: str, video_id: str) -> bool:
    item_id = _get_playlist_item_id(youtube, playlist_id, video_id)
    if not item_id:
        print(f"[WARN] プレイリストに存在しません: {video_id}")
        return False
    try:
        api_call_with_retry(lambda: youtube.playlistItems().delete(id=item_id).execute())
        return True
    except HttpError as e:
        print(f"[ERROR] 削除失敗 {video_id}: {e}")
        return False


# ── Core Logic ────────────────────────────────────────────────────────────────

def process_add(youtube, playlist: dict, history: list[dict]) -> tuple[int, int]:
    ok = skip = 0
    if not ADD_FILE.exists() or not ADD_FILE.read_text().strip():
        print("[INFO] add.txt なし/空 → スキップ")
        return ok, skip

    for video_id, title, url in parse_input(ADD_FILE):
        if was_previously_added(video_id, history, playlist["id"]):
            print(f"[INFO] 過去に追加済み（再追加）: {title or video_id}")
        time.sleep(INTERVAL_SEC)
        if api_add_video(youtube, playlist["id"], video_id):
            append_history(video_id, title, url, "add", playlist["id"])
            history.append({"video_id": video_id, "playlist_id": playlist["id"], "action": "add"})
            print(f"[OK] 追加: {title or video_id}")
            ok += 1
        else:
            skip += 1

    return ok, skip


def process_remove(youtube, playlist: dict) -> tuple[int, int]:
    ok = skip = 0
    if not REMOVE_FILE.exists() or not REMOVE_FILE.read_text().strip():
        print("[INFO] remove.txt なし/空 → スキップ")
        return ok, skip

    for video_id, title, url in parse_input(REMOVE_FILE):
        time.sleep(INTERVAL_SEC)
        if api_remove_video(youtube, playlist["id"], video_id):
            append_history(video_id, title, url, "remove", playlist["id"])
            print(f"[OK] 削除: {title or video_id}")
            ok += 1
        else:
            skip += 1

    return ok, skip


# ── Entry Point ───────────────────────────────────────────────────────────────

def main() -> None:
    init_csv()
    youtube = build_youtube_client()
    add_pl, remove_pl = choose_playlists(youtube)
    history = load_history()

    print(f"\n▶ 追加先 : {add_pl['title']}")
    print(f"▶ 削除元 : {remove_pl['title']}\n")

    add_ok, add_skip       = process_add(youtube, add_pl, history)
    remove_ok, remove_skip = process_remove(youtube, remove_pl)

    print("\n── 完了 ──────────────────────────────────")
    print(f"追加: {add_ok} 件成功 / {add_skip} 件スキップ")
    print(f"削除: {remove_ok} 件成功 / {remove_skip} 件スキップ")


if __name__ == "__main__":
    if "--auth-only" in sys.argv:
        build_youtube_client()
    else:
        main()
