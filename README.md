# Footprints — YouTube Playlist Sync Tool

OneTabからエクスポートしたURLをYouTubeプレイリストに同期するCLIツール。

## 必要なもの

- Docker
- Google アカウント（YouTubeプレイリストのオーナー）

---

## セットアップ（初回のみ）

### 1. Google Cloud Console で認証情報を作成

1. [Google Cloud Console](https://console.cloud.google.com) を開く
2. プロジェクトを作成（または既存のものを選択）
3. **APIとサービス → ライブラリ** を開き、`YouTube Data API v3` を検索して有効化
4. **APIとサービス → 認証情報** を開く
5. **認証情報を作成 → OAuth 2.0 クライアント ID** を選択
6. アプリケーションの種類: **デスクトップアプリ** を選択して作成
7. 作成されたクライアントの **JSONをダウンロード**
8. ダウンロードしたファイルをこのディレクトリに `client_secret.json` という名前で配置

> **補足**: 「OAuth同意画面」でアプリが未検証の場合、テストユーザーに自分のGmailアドレスを追加してください（APIとサービス → OAuth同意画面 → テストユーザー）

### 2. Dockerイメージをビルド

```bash
make build
```

### 3. 初回認証（token.json の生成）

```bash
make auth
```

ターミナルにURLが表示されます。そのURLをブラウザで開き、Googleアカウントでログイン後に表示される認証コードをターミナルに貼り付けてください。

`token.json` が自動生成され、次回以降は認証不要になります。

---

## 使い方

### 動画を追加する

`input/add.txt` にOneTabからエクスポートしたURLを貼り付けます。

```
https://www.youtube.com/watch?v=xxxxxx | 動画タイトル
https://youtu.be/yyyyyy | 別の動画
https://www.youtube.com/shorts/zzzzzz | ショート動画
```

フォーマットは `URL | タイトル` ですが、タイトルは省略可能です。

### 動画を削除する

`input/remove.txt` に同様の形式でURLを貼り付けます。

### 実行

```bash
make run
```

起動後、十字キーでプレイリストを選択します。

```
追加先プレイリストを選択:
❯ AI学習用  (PLxxxxxxxxxx)
  技術メモ  (PLyyyyyyyyyy)
  Watch Later  (PLzzzzzzzzz)

削除元プレイリストを選択:
  AI学習用  (PLxxxxxxxxxx)
  技術メモ  (PLyyyyyyyyyy)
❯ Watch Later  (PLzzzzzzzzz)
```

前回選んだプレイリストがデフォルトになります。同じ設定で続ける場合はEnterを2回押すだけです。

---

## コマンド一覧

| コマンド | 説明 |
|---|---|
| `make build` | Dockerイメージをビルド（初回・requirements.txt変更時に実行） |
| `make auth` | 初回OAuth2認証・`token.json` 生成 |
| `make run` | プレイリスト選択 → 追加・削除を実行 |

### API呼び出し間隔の調整

```bash
make run INTERVAL_SECONDS=2.0
```

デフォルトは1.0秒です。Quota超過が気になる場合は増やしてください。

---

## ファイル構成

```
.
├── Dockerfile
├── Makefile
├── README.md
├── main.py
├── requirements.txt
├── client_secret.json   # 手動配置・Git管理外
├── token.json           # 自動生成・Git管理外
├── config.json          # プレイリスト選択の記憶・Git管理外
├── playlist_history.csv # 全操作履歴・Git管理外
└── input/
    ├── add.txt          # 追加対象URL
    └── remove.txt       # 削除対象URL
```

## 操作履歴

`playlist_history.csv` に全操作が記録されます。

| カラム | 内容 |
|---|---|
| timestamp | 操作日時 |
| video_id | YouTubeの動画ID |
| title | 動画タイトル |
| url | 動画URL |
| action | `add` または `remove` |
| playlist_id | 操作対象のプレイリストID |
