"""CLI controller — orchestrates auth, playlist selection, and sync."""
import sys
from pathlib import Path

import questionary

from domain.models import ParseResult
from domain.parser import parse_input
from repository.config import load_config, save_config
from repository.history import init_csv, load_history
from repository.youtube import build_youtube_client, fetch_playlists
from service.sync import print_summary, process_add, process_remove

BASE_DIR = Path(__file__).parent.parent
INPUT_DIR = BASE_DIR / "input"
DATA_DIR = Path("/data/youtube")
CSV_PATH = DATA_DIR / "playlist_history.csv"
CONFIG_PATH = BASE_DIR / "config.json"
CREDENTIALS_PATH = BASE_DIR / "client_secret.json"
TOKEN_PATH = BASE_DIR / "token.json"


def choose_playlists(youtube, config_path: Path) -> tuple[dict, dict]:
    playlists = fetch_playlists(youtube)
    if not playlists:
        print("[ERROR] プレイリストが見つかりません。YouTube でプレイリストを作成してから再実行してください。")
        sys.exit(1)

    config = load_config(config_path)
    choices = [questionary.Choice(title=p["title"], value=p) for p in playlists]

    def _default(key: str) -> dict:
        last_id = config.get(key)
        if last_id:
            for p in playlists:
                if p["id"] == last_id:
                    return p
        return playlists[0]

    print("\n▶ 追加先プレイリストを選択してください（↑↓キーで移動、Enterで決定）:")
    add_pl = questionary.select(
        "追加先:", choices=choices, default=_default("last_add_playlist_id")
    ).ask()

    print("\n▶ 削除対象プレイリストを選択してください（↑↓キーで移動、Enterで決定）:")
    remove_pl = questionary.select(
        "削除対象:", choices=choices, default=_default("last_remove_playlist_id")
    ).ask()

    if not add_pl or not remove_pl:
        print("[INFO] キャンセルされました。")
        sys.exit(0)

    save_config(config_path, {
        "last_add_playlist_id": add_pl["id"],
        "last_remove_playlist_id": remove_pl["id"],
    })

    return add_pl, remove_pl


def main(
    credentials_path: Path = CREDENTIALS_PATH,
    token_path: Path = TOKEN_PATH,
    csv_path: Path = CSV_PATH,
    config_path: Path = CONFIG_PATH,
    add_file: Path = INPUT_DIR / "add.txt",
    remove_file: Path = INPUT_DIR / "remove.txt",
) -> None:
    if not credentials_path.exists():
        print(
            f"[ERROR] {credentials_path} が見つかりません。\n"
            "README を参照して client_secret.json を配置してください。"
        )
        sys.exit(1)

    print("YouTube API 認証中...")
    youtube = build_youtube_client(credentials_path, token_path)

    init_csv(csv_path)
    history = load_history(csv_path)

    add_pl, remove_pl = choose_playlists(youtube, config_path)

    print(f"\n追加先    : {add_pl['title']}")
    print(f"削除対象  : {remove_pl['title']}\n")

    def _safe_parse(path: Path) -> ParseResult:
        if path.exists() and path.read_text(encoding="utf-8").strip():
            return parse_input(path)
        return ParseResult()

    parse_add = _safe_parse(add_file)
    parse_remove = _safe_parse(remove_file)

    add_result = process_add(youtube, add_pl, history, add_file, csv_path)
    remove_result = process_remove(youtube, remove_pl, remove_file, csv_path)

    print_summary(parse_add, parse_remove, add_result, remove_result)
