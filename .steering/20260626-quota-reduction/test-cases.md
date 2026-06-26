# test-cases.md

テストファイル単位でケースを定義する。
既存テストの変更点と新規テストを明示する。

---

## 1. `tests/test_api.py`（既存ファイルの変更）

### `TestApiCallWithRetry`

| # | 種別 | ケース名 | 入力 | 期待値 | 確認方法 |
|---|---|---|---|---|---|
| 1 | 正常系 | 成功時は結果を返す | fn が `"ok"` を返す | `"ok"` が返る | 戻り値を assert |
| 2 | 異常系 | **quotaExceeded (403) で `QuotaExceededError` を raise** | fn が `HttpError(403, "quotaExceeded")` を raise | `QuotaExceededError` が raise される | `pytest.raises(QuotaExceededError)` |
| 3 | 異常系 | quota 以外の 403 は re-raise | fn が `HttpError(403, "forbidden")` を raise | `HttpError` が re-raise される | `pytest.raises(HttpError)` |
| 4 | 異常系 | 404 は re-raise | fn が `HttpError(404)` を raise | `HttpError` が re-raise される | `pytest.raises(HttpError)` |
| 5 | 異常系 | 500 は re-raise | fn が `HttpError(500)` を raise | `HttpError` が re-raise される | `pytest.raises(HttpError)` |

> **変更点:** 既存の `test_retries_on_quota_exceeded`（リトライ後に成功することを検証）を
> `test_raises_quota_exceeded_error` に差し替える。`time.sleep` のモックも不要になる。

---

### `TestQuotaResetMessage`（新規追加）

| # | 種別 | ケース名 | 入力 | 期待値 | 確認方法 |
|---|---|---|---|---|---|
| 6 | 正常系 | リセット時刻メッセージが文字列として返る | なし（現在時刻に依存） | 文字列が返り、`"クォータ"` と `"太平洋時間"` が含まれる | `in` で部分文字列を確認 |
| 7 | 正常系 | 残り時間が 0〜23 時間の範囲の数字を含む | `freezegun` で時刻固定 | メッセージ内の時間数字が正しい | 固定時刻でメッセージ内容を assert |

---

### `TestFetchPlaylistVideoIds`（新規追加）

| # | 種別 | ケース名 | 入力 | 期待値 | 確認方法 |
|---|---|---|---|---|---|
| 8 | 異常系 | クォータ超過時に `QuotaExceededError` が伝播する | `playlistItems().list()` が `HttpError(403, "quotaExceeded")` を raise | `QuotaExceededError` が raise される | `pytest.raises(QuotaExceededError)` |

---

## 2. `tests/test_cache.py`（新規ファイル）

### `TestLoadPlaylistCache`

| # | 種別 | ケース名 | 入力 | 期待値 | 確認方法 |
|---|---|---|---|---|---|
| 1 | 正常系 | キャッシュファイルがない場合 `None` を返す | キャッシュファイル未作成 | `None` が返る | `assert result is None` |
| 2 | 正常系 | TTL 内のキャッシュから video_id セットを返す | `fetched_at` = 現在より 1 時間前 | `set[str]` が返り、保存した ID を含む | `assert video_ids == result` |
| 3 | 準正常系 | TTL 超過のキャッシュは `None` を返す | `fetched_at` = 現在より 24 時間前 | `None` が返る | `assert result is None` |
| 4 | 準正常系 | `fetched_at` がちょうど TTL と等しい場合は無効 | `fetched_at` = 現在より 23 時間前（`CACHE_TTL_HOURS=23`） | `None` が返る | `assert result is None` |

---

### `TestSavePlaylistCache`

| # | 種別 | ケース名 | 入力 | 期待値 | 確認方法 |
|---|---|---|---|---|---|
| 5 | 正常系 | キャッシュファイルが作成される | `video_ids={"abc", "def"}` | ファイルが存在し、両 ID が含まれる | `cache_path.exists()` と JSON 内容を assert |
| 6 | 正常系 | `fetched_at` が現在時刻（UTC）で記録される | `freezegun` で時刻固定 | JSON の `fetched_at` フィールドが固定時刻と一致 | ISO8601 文字列を assert |
| 7 | 正常系 | 既存キャッシュを上書きする | 2 回 `save_playlist_cache` を呼ぶ | 2 回目の内容で上書きされている | ファイル内容を assert |

---

### `TestAddToCache`

| # | 種別 | ケース名 | 入力 | 期待値 | 確認方法 |
|---|---|---|---|---|---|
| 8 | 正常系 | キャッシュが存在する場合、video_id が追加される | 既存キャッシュ `{"abc"}` に `"xyz"` を追加 | キャッシュが `{"abc", "xyz"}` になる | ファイルを読み込んで assert |
| 9 | 準正常系 | キャッシュファイルが存在しない場合は何もしない | キャッシュなし | クラッシュしない・ファイルが作成されない | 例外が raise されないことを確認 |
| 10 | 準正常系 | 既に存在する video_id を追加しても重複しない | `{"abc"}` に `"abc"` を追加 | キャッシュが `{"abc"}` のまま | ファイル内容を assert |

---

### `TestRemoveFromCache`

| # | 種別 | ケース名 | 入力 | 期待値 | 確認方法 |
|---|---|---|---|---|---|
| 11 | 正常系 | キャッシュが存在する場合、video_id が削除される | 既存キャッシュ `{"abc", "xyz"}` から `"abc"` を削除 | キャッシュが `{"xyz"}` になる | ファイルを読み込んで assert |
| 12 | 準正常系 | キャッシュファイルが存在しない場合は何もしない | キャッシュなし | クラッシュしない | 例外が raise されないことを確認 |
| 13 | 準正常系 | 存在しない video_id を削除しても何も起きない | `{"abc"}` から `"xyz"` を削除 | キャッシュが `{"abc"}` のまま | ファイル内容を assert |

---

## 3. `tests/test_process.py`（既存ファイルの変更）

### `TestProcessAdd`（追加ケース）

既存ケースに加えて以下を追加する。`process_add` のシグネチャに `cache_dir` 引数が加わる点に注意。

| # | 種別 | ケース名 | 入力 | 期待値 | 確認方法 |
|---|---|---|---|---|---|
| 1 | 正常系 | キャッシュヒット時は `fetch_playlist_video_ids` を呼ばない | 有効なキャッシュあり | `fetch_playlist_video_ids` が呼ばれない | `mock.assert_not_called()` |
| 2 | 正常系 | キャッシュミス時は API から取得してキャッシュを保存する | キャッシュなし | `fetch_playlist_video_ids` が 1 回呼ばれ、キャッシュファイルが作成される | mock の呼び出し回数 + ファイル存在確認 |
| 3 | 正常系 | 追加成功後にキャッシュへ video_id が追加される | キャッシュあり・1 件追加成功 | キャッシュファイルに追加した video_id が含まれる | ファイル内容を assert |
| 4 | 異常系 | `fetch_playlist_video_ids` が `QuotaExceededError` を raise した場合、re-raise する | キャッシュなし・API が `QuotaExceededError` を raise | `QuotaExceededError` が呼び出し元に伝播する | `pytest.raises(QuotaExceededError)` |
| 5 | 異常系 | `api_add_video` が `QuotaExceededError` を raise した場合、re-raise する | キャッシュあり・insert が `QuotaExceededError` を raise | `QuotaExceededError` が呼び出し元に伝播する | `pytest.raises(QuotaExceededError)` |

---

### `TestProcessRemove`（追加ケース）

| # | 種別 | ケース名 | 入力 | 期待値 | 確認方法 |
|---|---|---|---|---|---|
| 6 | 正常系 | 削除成功後にキャッシュから video_id が除去される | キャッシュあり・1 件削除成功 | キャッシュファイルから削除した video_id が消える | ファイル内容を assert |

---

## モック方針（補足）

| 対象 | モック方法 |
|---|---|
| `fetch_playlist_video_ids` | `patch("service.sync.fetch_playlist_video_ids", return_value=set())` |
| `api_add_video` | `yt.playlistItems().insert().execute.return_value = {}` |
| `QuotaExceededError` の再現 | `patch("service.sync.fetch_playlist_video_ids", side_effect=QuotaExceededError())` |
| キャッシュ読み書き | `tmp_path` フィクスチャで実ファイルを使用（モック不要） |
| 時刻固定 | `freezegun.freeze_time("2026-06-26T10:00:00+00:00")` |
