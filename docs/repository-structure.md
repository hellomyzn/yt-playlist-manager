# リポジトリ構造定義書

## ディレクトリ構成

```
yt-playlist-manager/
├── .devcontainer/               # Dev Container 設定（VS Code Remote Containers）
│   ├── devcontainer.json
│   ├── docker-compose.yml
│   ├── Makefile
│   └── .env.template
├── .steering/                   # 作業単位のステアリングドキュメント
│   └── [YYYYMMDD]-[タイトル]/
│       ├── requirements.md
│       ├── design.md
│       ├── test-cases.md
│       ├── tasklist.md
│       ├── blockers.md          # (オプション)
│       └── decisions.md         # (オプション)
├── .vscode/                     # VS Code 設定
│   ├── launch.json
│   └── settings.json
├── docs/                        # 永続的ドキュメント
│   ├── product-requirements.md  # プロダクト要求定義書
│   ├── functional-design.md     # 機能設計書
│   ├── architecture.md          # 技術仕様書
│   ├── repository-structure.md  # リポジトリ構造定義書（本ファイル）
│   ├── development-guidelines.md# 開発ガイドライン
│   └── glossary.md              # ユビキタス言語定義
├── infra/
│   └── docker/python/
│       ├── Dockerfile
│       └── docker-entrypoint.sh
├── src/                         # アプリケーションソースコード
│   ├── main.py                  # エントリーポイント
│   ├── pyproject.toml           # Poetry 依存関係定義
│   ├── controller/
│   │   ├── __init__.py
│   │   └── cli.py               # CLIオーケストレーター
│   ├── domain/
│   │   ├── __init__.py
│   │   ├── models.py            # データクラス定義
│   │   └── parser.py            # URL解析・入力パース
│   ├── repository/
│   │   ├── __init__.py
│   │   ├── config.py            # config.json 読み書き
│   │   ├── history.py           # playlist_history.csv 読み書き
│   │   └── youtube.py           # YouTube Data API v3 クライアント
│   ├── service/
│   │   ├── __init__.py
│   │   └── sync.py              # 追加・削除処理・サマリー表示
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── test_video_id.py     # extract_video_id のテスト
│   │   ├── test_parse_input.py  # parse_input のテスト
│   │   ├── test_csv_history.py  # CSV履歴管理のテスト
│   │   ├── test_api.py          # YouTube API関数のテスト
│   │   ├── test_process.py      # process_add / process_remove のテスト
│   │   ├── test_fetch_playlists.py
│   │   ├── test_config.py
│   │   └── test_summary.py
│   └── input/
│       ├── .gitkeep
│       ├── add.txt              # Git管理外（ユーザーが貼り付け）
│       └── remove.txt           # Git管理外（ユーザーが貼り付け）
├── .env                         # Git管理外
├── .env.template
├── .gitignore
├── CLAUDE.md                    # プロジェクトメモリ（AI向け指示）
├── docker-compose.yml
├── Makefile
└── README.md
```

---

## ディレクトリの役割

### `src/` — アプリケーション本体

コンテナ内 `/opt/work` にマウントされる。レイヤードアーキテクチャを採用。

| ディレクトリ | 役割 |
|---|---|
| `controller/` | ユーザーインターフェース。認証・UI・オーケストレーション |
| `domain/` | ビジネスロジック。URL解析・データモデル。外部依存なし |
| `service/` | ユースケース層。追加・削除フローの制御 |
| `repository/` | データアクセス層。YouTube API・CSV・config.json |
| `tests/` | ユニット・統合テスト |
| `input/` | ユーザーが貼り付けるURLファイル置き場 |

### `docs/` — 永続的ドキュメント

アプリケーションの「何を作るか」「どう作るか」を定義する。基本設計が変わらない限り更新不要。

### `.steering/` — 作業単位のドキュメント

特定の開発作業ごとに新しいディレクトリを作成する。作業完了後は履歴として保持。

---

## Git管理外ファイル

以下のファイルは `.gitignore` によりGit管理対象外:

| ファイル | 理由 |
|---|---|
| `src/client_secret.json` | OAuth2クライアントシークレット（機密情報） |
| `src/token.json` | アクセストークン（機密情報） |
| `src/config.json` | 前回選択プレイリスト（個人設定） |
| `src/input/add.txt` | ユーザーが都度貼り付けるURL |
| `src/input/remove.txt` | ユーザーが都度貼り付けるURL |
| `.env` | 環境変数（機密情報を含む可能性） |
| `playlist_history.csv` | 操作履歴（外部ボリュームにマウント） |

---

## 外部ボリューム

| コンテナ内パス | ホストパス | 内容 |
|---|---|---|
| `/data/youtube/` | `../../footprints/youtube/` | `playlist_history.csv` の永続化先 |
