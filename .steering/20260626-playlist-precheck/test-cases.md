# テストケース一覧: プレイリスト事前チェック機能

---

## 1. `fetch_playlist_video_ids(youtube, playlist_id) -> set[str]`

### 正常系

| # | 状況 | 期待値 |
|---|---|---|
| N-1 | プレイリストに動画が2件 | `{"AAAAAAAAAAa", "BBBBBBBBBBb"}` |

### 準正常系

| # | 状況 | 期待値 | 理由 |
|---|---|---|---|
| Q-1 | プレイリストが空（items=[]） | `set()` | 空セット |
| Q-2 | 2ページに分かれている（nextPageToken あり） | 全件の set | ページネーション対応 |

---

## 2. `process_add` の更新テスト

チェック順序: ① プレイリスト既存 → ② CSV既存 → ③ 追加

### モック方針

- `fetch_playlist_video_ids` → `patch("service.sync.fetch_playlist_video_ids", return_value=set(...))`
- `questionary.confirm` → `patch("service.sync.questionary.confirm")`
- `time.sleep` → `patch("service.sync.time.sleep")`

### 正常系

| # | 状況 | 期待値 |
|---|---|---|
| N-1 | 既存なし（API・CSV両方） → 全件追加成功 | `ok=2`, 他すべて空 |

### 準正常系

| # | 状況 | 期待値 | 理由 |
|---|---|---|---|
| Q-1 | add.txt が空または存在しない | 全フィールド0/空 | スキップ |
| Q-2 | ①プレイリスト既存 → 自動スキップ | `already_in_playlist` に記録, 確認なし | 確認不要 |
| Q-3 | ①プレイリスト既存なし ②CSV既存 → ユーザーが Yes | `ok=2, confirmed_skip=0` | 追加される |
| Q-4 | ①プレイリスト既存なし ②CSV既存 → ユーザーが No | `confirmed_skip=1, ok=1` | 1件スキップ・1件追加 |
| Q-5 | プレイリスト既存なし・CSV既存なしで追加したが409（競合フォールバック） | `already_in_playlist` に記録 | レアケース |

### 異常系

| # | 状況 | 期待値 | 理由 |
|---|---|---|---|
| E-1 | 追加APIが500エラー | `api_errors` に記録 | クラッシュしない |

### 変更されるテスト

| テスト名 | 変更内容 |
|---|---|
| `test_all_success` | `fetch_playlist_video_ids` を `set()` でモック追加 |
| `test_409_collected_as_already_in_playlist` | `fetch_playlist_video_ids` を `set()` でモック追加 |
| `test_previously_added_user_confirms` | → `test_already_in_playlist_user_confirms` に改名・APIモック追加 |
| `test_previously_added_user_declines` | → `test_already_in_playlist_user_declines` に改名・APIモック追加 |
| `test_api_error_collected` | `fetch_playlist_video_ids` を `set()` でモック追加 |
