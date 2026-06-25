# 設計

## 実行環境

- **ベース**: polydock docker-python（docker-compose + Poetry）
- **コンテナ**: `docker-compose exec workspace python main.py`
- **ソースマウント**: `src/` → コンテナ内 `/opt/work`

## ディレクトリ構成

```
yt-playlist-manager/
├── .devcontainer/
├── .steering/
├── .vscode/
├── .gitignore
├── .env                        # Git管理外
├── .env.template
├── docker-compose.yml
├── infra/
│   └── docker/python/
│       ├── Dockerfile
│       └── docker-entrypoint.sh
├── Makefile
├── README.md
└── src/
    ├── pyproject.toml
    ├── main.py                  # エントリーポイント
    ├── input/
    │   ├── add.txt              # Git管理外
    │   └── remove.txt           # Git管理外
    ├── client_secret.json       # Git管理外（手動配置）
    ├── token.json               # Git管理外（自動生成）
    ├── config.json              # Git管理外（前回選択保存）
    ├── playlist_history.csv     # Git管理外（操作履歴）
    ├── common/
    │   ├── config/              # INI設定管理
    │   ├── decorator/           # 例外デコレータ
    │   ├── exceptions/          # カスタム例外
    │   ├── log/                 # ロガー
    │   └── retry/               # リトライユーティリティ
    ├── tests/
    │   ├── test_video_id.py     # extract_video_id のテスト
    │   ├── test_parse_input.py  # parse_input のテスト
    │   ├── test_csv_history.py  # CSV履歴管理のテスト
    │   ├── test_api.py          # YouTube API関数のテスト
    │   └── test_process.py      # process_add/remove のテスト
    └── utils/
        ├── datetime_parser.py
        └── singleton.py
```

## 主要コンポーネント

### 認証（`build_youtube_client()`）
- `token.json` が存在すれば読み込み、期限切れなら自動リフレッシュ
- 存在しない場合: `InstalledAppFlow` でコンソール認証（URLをターミナルに出力 → コード入力）
- `--auth-only` フラグで認証のみ実行

### URL解析（`extract_video_id(url)`）
- `urllib.parse` でクエリパラメータを正確に解析（regexではなく）
- 対応形式: `watch?v=`, `youtu.be/`, `shorts/`, `embed/`, `v/`
- video_id は11文字英数字のバリデーションを行う

### 入力ファイルパース（`parse_input(path)`）
- `URL | Title` 形式をパース（タイトルは省略可）
- 同一ファイル内の重複video_idを除去（先勝ち）
- 無効URLはWARNログを出力してスキップ

### プレイリスト選択（`choose_playlists(youtube)`）
- `playlists.list(mine=True)` でAPIからプレイリスト一覧を取得
- `questionary.select()` で十字キー選択UI
- `config.json` から前回選択をデフォルトとして表示
- 選択後に `config.json` を更新

### YouTube API操作
- `api_add_video()`: `playlistItems.insert` (50ユニット)
- `api_remove_video()`: `playlistItems.list` → `playlistItems.delete` (1 + 50ユニット)
- `api_call_with_retry()`: quota超過（403 quotaExceeded）時は `QUOTA_WAIT` 秒ポーリング

### CSV履歴管理
- スキーマ: `timestamp, video_id, title, url, action, playlist_id`
- 存在確認はローカルCSVで行う（API呼び出し不要）
- 追加成功後にCSVへ追記 + インメモリhistoryも更新（同一セッション内の重複チェックのため）

## エラーハンドリング方針

| エラー | 対応 |
|---|---|
| 409 Conflict（追加済み） | WARNログ、スキップ、クリーンアップしない |
| 404 Not Found（削除対象なし） | WARNログ、スキップ |
| 403 quotaExceeded | ポーリングで再試行（Ctrl+Cで中断可） |
| その他HTTPError | ERRORログ、スキップ |
| video_id抽出失敗 | WARNログ、スキップ |
| 重複video_id | INFOログ、スキップ（先勝ち） |

## データスキーマ

### `playlist_history.csv`

| カラム | 型 | 例 |
|---|---|---|
| timestamp | YYYY-MM-DD HH:MM:SS | 2026-06-26 10:00:00 |
| video_id | 11文字英数字 | dQw4w9WgXcY |
| title | 文字列（空可） | AI入門動画 |
| url | URL文字列 | https://youtube.com/watch?v=... |
| action | add / remove | add |
| playlist_id | YouTubeプレイリストID | PLxxxxxxxxxx |

### `config.json`

```json
{
  "last_add_playlist_id": "PLxxxxxxxxxx",
  "last_remove_playlist_id": "PLyyyyyyyyyy"
}
```
