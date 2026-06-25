import re
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from domain.models import ParseResult


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


def parse_input(path: Path) -> ParseResult:
    seen: set[str] = set()
    result = ParseResult()
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        parts = line.split("|", 1)
        url = parts[0].strip()
        title = parts[1].strip() if len(parts) > 1 else ""
        vid = extract_video_id(url)
        if not vid:
            result.invalid_lines.append(line)
            continue
        if vid in seen:
            result.duplicate_ids.append(vid)
            continue
        seen.add(vid)
        result.items.append((vid, title, url))
    return result
