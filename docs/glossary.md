# ユビキタス言語定義

このプロジェクトで使用する用語の定義。コード・ドキュメント・会話で一貫して使用する。

---

## 動画・URL関連

| 用語 | 定義 |
|---|---|
| **video_id** | YouTubeの動画を一意に識別する11文字の英数字文字列（例: `dQw4w9WgXcY`）。URLから抽出される |
| **URL** | OneTabからエクスポートされたYouTube動画のURL。`watch?v=`, `youtu.be/`, `shorts/` 等の複数形式に対応 |
| **OneTab形式** | OneTabがエクスポートする `URL | タイトル` の形式。タイトルは省略可能 |
| **無効URL** | `extract_video_id` が `None` を返したURL。video_idを抽出できない行 |
| **重複video_id** | 同一の入力ファイル内に複数回登場した video_id。先勝ちで1件のみ処理される |

---

## プレイリスト関連

| 用語 | 定義 |
|---|---|
| **playlist_id** | YouTubeプレイリストを一意に識別するID（例: `PLxxxxxxxxxx`） |
| **追加先プレイリスト** | `add.txt` の動画を追加する対象プレイリスト。実行時に選択する |
| **削除元プレイリスト** | `remove.txt` の動画を削除する対象プレイリスト。実行時に選択する |
| **プレイリスト既存** | API事前チェック（`fetch_playlist_video_ids`）でプレイリストに既に動画が存在する状態。自動スキップされる |

---

## 処理・状態関連

| 用語 | 定義 |
|---|---|
| **追加成功 (`ok`)** | `api_add_video` が成功し、履歴CSVに記録された件数 |
| **削除成功 (`ok`)** | `api_remove_video` が成功し、履歴CSVに記録された件数 |
| **already_in_playlist** | API事前チェックでプレイリスト既存と判明し、自動スキップされた動画リスト |
| **confirmed_skip** | CSV履歴に過去追加の記録があり、ユーザーが「No」を選択してスキップした件数 |
| **not_found** | 削除対象として指定したが、プレイリストに存在しなかった動画リスト |
| **api_errors** | APIエラー（409/404以外）で処理できなかった動画リスト |
| **Quota超過** | YouTube Data API の日次Quota（10,000 units）を超えた状態。`QUOTA_WAIT` 秒待機して再試行 |

---

## ファイル関連

| 用語 | 定義 |
|---|---|
| **add.txt** | 追加したいYouTube動画URLをOneTab形式で貼り付けるファイル（`src/input/add.txt`） |
| **remove.txt** | 削除したいYouTube動画URLをOneTab形式で貼り付けるファイル（`src/input/remove.txt`） |
| **playlist_history.csv** | 全追加・削除操作の履歴を記録するCSVファイル。ローカルの正本 |
| **config.json** | 前回選択したプレイリストIDを保存するJSONファイル |
| **client_secret.json** | Google Cloud ConsoleからダウンロードするOAuth2クライアントシークレット |
| **token.json** | OAuth2認証後に自動生成されるアクセストークン・リフレッシュトークン |

---

## アーキテクチャ用語

| 用語 | 定義 |
|---|---|
| **ParseResult** | `parse_input` の返り値。`items`（処理対象）・`invalid_lines`・`duplicate_ids` を含む |
| **AddResult** | `process_add` の返り値。追加処理の結果を集約するデータクラス |
| **RemoveResult** | `process_remove` の返り値。削除処理の結果を集約するデータクラス |
| **ステアリングドキュメント** | `.steering/` 以下に作業単位で作成する一時的なドキュメント群 |
| **永続的ドキュメント** | `docs/` 以下に配置する、アプリケーション基本設計を定義するドキュメント群 |
| **処理の取りこぼしゼロ原則** | ユーザーが意図した追加・削除がサイレントにスキップされることを禁止する設計原則 |
