from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

from googleapiclient.errors import HttpError

SCOPES = ["https://www.googleapis.com/auth/youtube"]


class QuotaExceededError(Exception):
    """YouTube API の日次クォータ超過時に raise する。"""
    pass


def build_youtube_client(credentials_path: Path, token_path: Path):
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build

    creds = None
    if token_path.exists():
        creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(str(credentials_path), SCOPES)
            # Docker環境向け手動フロー（ブラウザ不要）
            flow.redirect_uri = "urn:ietf:wg:oauth:2.0:oob"
            auth_url, _ = flow.authorization_url(prompt="consent")
            print(f"\n以下のURLをブラウザで開いてください:\n\n  {auth_url}\n")
            code = input("表示された認証コードを貼り付けてください: ").strip()
            flow.fetch_token(code=code)
            creds = flow.credentials
        token_path.write_text(creds.to_json(), encoding="utf-8")

    return build("youtube", "v3", credentials=creds)


def fetch_playlists(youtube) -> list[dict]:
    res = api_call_with_retry(lambda: youtube.playlists().list(part="snippet", mine=True, maxResults=50).execute())
    return [
        {"id": item["id"], "title": item["snippet"]["title"]}
        for item in res.get("items", [])
    ]


def fetch_playlist_video_ids(youtube, playlist_id: str) -> set[str]:
    ids: set[str] = set()
    next_token = None
    while True:
        kwargs: dict = dict(part="snippet", playlistId=playlist_id, maxResults=50)
        if next_token:
            kwargs["pageToken"] = next_token
        res = api_call_with_retry(lambda: youtube.playlistItems().list(**kwargs).execute())
        for item in res.get("items", []):
            ids.add(item["snippet"]["resourceId"]["videoId"])
        next_token = res.get("nextPageToken")
        if not next_token:
            break
    return ids


def quota_reset_message() -> str:
    pacific = ZoneInfo("America/Los_Angeles")
    now_pt = datetime.now(pacific)
    next_reset = (now_pt + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
    delta = next_reset - now_pt
    hours, rem = divmod(int(delta.total_seconds()), 3600)
    minutes = rem // 60
    return (
        f"[ERROR] YouTube API の1日のクォータ上限（10,000ユニット）に達しました。\n"
        f"クォータは太平洋時間の午前0時にリセットされます。\n"
        f"約 {hours}時間{minutes}分後（PT {next_reset.strftime('%H:%M')}）に再実行してください。"
    )


def api_call_with_retry(fn):
    try:
        return fn()
    except HttpError as e:
        if e.resp.status == 403 and b"quotaExceeded" in e.content:
            raise QuotaExceededError()
        raise


def api_add_video(youtube, playlist_id: str, video_id: str) -> bool:
    """Returns True on success, False if already in playlist (409), raises on other errors."""
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
            return False
        raise


def _get_playlist_item_id(youtube, playlist_id: str, video_id: str) -> str | None:
    res = api_call_with_retry(lambda: youtube.playlistItems().list(
        part="id", playlistId=playlist_id, videoId=video_id
    ).execute())
    items = res.get("items", [])
    return items[0]["id"] if items else None


def api_remove_video(youtube, playlist_id: str, video_id: str) -> bool:
    """Returns True on success, False if not in playlist, raises on API errors."""
    item_id = _get_playlist_item_id(youtube, playlist_id, video_id)
    if not item_id:
        return False
    api_call_with_retry(lambda: youtube.playlistItems().delete(id=item_id).execute())
    return True
