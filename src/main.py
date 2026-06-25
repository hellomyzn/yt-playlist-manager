"""Footprints - YouTube Playlist Sync Tool"""
import re
import time
from urllib.parse import parse_qs, urlparse


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
