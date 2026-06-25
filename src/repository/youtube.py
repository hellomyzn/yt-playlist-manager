import time

from googleapiclient.errors import HttpError

QUOTA_WAIT = 60


def api_call_with_retry(fn):
    while True:
        try:
            return fn()
        except HttpError as e:
            if e.resp.status == 403 and b"quotaExceeded" in e.content:
                print(f"[WARN] Quota超過。{QUOTA_WAIT}秒後に再試行... (Ctrl+C で中断)")
                time.sleep(QUOTA_WAIT)
            else:
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
