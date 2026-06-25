"""Footprints - YouTube Playlist Sync Tool"""
import sys
from pathlib import Path


def _auth_only() -> None:
    from repository.youtube import build_youtube_client
    base = Path(__file__).parent
    build_youtube_client(base / "client_secret.json", base / "token.json")
    print("認証完了。token.json が生成されました。次回から make run が使えます。")


if __name__ == "__main__":
    if "--auth-only" in sys.argv:
        _auth_only()
    else:
        from controller.cli import main
        main()
