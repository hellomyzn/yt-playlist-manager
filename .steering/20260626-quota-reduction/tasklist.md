# tasklist.md

TDDサイクル（Red → Green → Refactor → Commit）単位でタスクを定義する。
各タスクは前のタスクが完了（テスト通過・コミット済み）してから開始する。

---

## タスク一覧

| # | タスク | ステータス |
|---|---|---|
| 1 | `QuotaExceededError` 追加・`api_call_with_retry` リトライ廃止 | 未着手 |
| 2 | `fetch_playlist_video_ids` を `api_call_with_retry` でラップ | 未着手 |
| 3 | `quota_reset_message()` 実装 | 未着手 |
| 4 | `repository/cache.py` 新規実装 | 未着手 |
| 5 | `process_add` キャッシュ対応 | 未着手 |
| 6 | `process_remove` キャッシュ対応 | 未着手 |
| 7 | `controller/cli.py` `QuotaExceededError` キャッチ | 未着手 |
| 8 | `docker-compose.yml` ボリュームマウント変更 | 未着手 |

---

## タスク詳細

---

### タスク 1: `QuotaExceededError` 追加・`api_call_with_retry` リトライ廃止

**変更ファイル:** `src/repository/youtube.py`, `src/tests/test_api.py`

#### Red
`tests/test_api.py` の `TestApiCallWithRetry` を以下のように変更する：
- `test_retries_on_quota_exceeded` を削除
- `test_raises_quota_exceeded_error_on_quota_exceeded` を追加（`QuotaExceededError` が raise されることを検証）
- テストを実行して失敗することを確認

#### Green
`repository/youtube.py` を変更する：
- `QuotaExceededError(Exception)` クラスを追加
- `api_call_with_retry` の `while True` ループを廃止し、クォータ超過時に `QuotaExceededError` を raise

#### Refactor
- `youtube.py` から不要になった `QUOTA_WAIT = 60` 定数と `import time` を削除
- `test_api.py` から `patch("repository.youtube.time.sleep")` のモックを削除

#### Commit
```
feat: QuotaExceededError 追加・api_call_with_retry のリトライ廃止
```

---

### タスク 2: `fetch_playlist_video_ids` を `api_call_with_retry` でラップ

**変更ファイル:** `src/repository/youtube.py`, `src/tests/test_api.py`

#### Red
`tests/test_api.py` に `TestFetchPlaylistVideoIds` クラスを追加する：
- `test_raises_quota_exceeded_when_list_fails`: `playlistItems().list().execute` が `HttpError(403, "quotaExceeded")` を raise したとき `QuotaExceededError` が伝播することを検証

#### Green
`repository/youtube.py` の `fetch_playlist_video_ids` 内の API 呼び出しを `api_call_with_retry` でラップする：

```python
res = api_call_with_retry(lambda: youtube.playlistItems().list(**kwargs).execute())
```

#### Commit
```
fix: fetch_playlist_video_ids のクォータ超過を QuotaExceededError に変換
```

---

### タスク 3: `quota_reset_message()` 実装

**変更ファイル:** `src/repository/youtube.py`, `src/tests/test_api.py`

#### Red
`tests/test_api.py` に `TestQuotaResetMessage` クラスを追加する：
- `test_returns_string_containing_key_phrases`: 戻り値に `"クォータ"` と `"太平洋時間"` が含まれる
- `test_returns_correct_remaining_hours`: `freezegun` で時刻を固定し、残り時間の数字が正しい

#### Green
`repository/youtube.py` に `quota_reset_message()` を実装する：
- `zoneinfo.ZoneInfo("America/Los_Angeles")` で太平洋時間の翌日 0:00 を計算
- 残り時間（時・分）を含むメッセージ文字列を返す

#### Commit
```
feat: クォータリセット時刻メッセージ表示関数を追加
```

---

### タスク 4: `repository/cache.py` 新規実装

**変更ファイル:** `src/repository/cache.py`（新規）, `src/tests/test_cache.py`（新規）

#### Red
`tests/test_cache.py` を新規作成し、以下の全13ケースを記述する（`test-cases.md` 参照）：
- `TestLoadPlaylistCache`（4ケース）
- `TestSavePlaylistCache`（3ケース）
- `TestAddToCache`（3ケース）
- `TestRemoveFromCache`（3ケース）

テストを実行してすべて失敗することを確認（`ImportError` で失敗すればOK）。

#### Green
`repository/cache.py` を新規作成し、以下を実装する：
- `load_playlist_cache(playlist_id, cache_dir) -> set[str] | None`
- `save_playlist_cache(playlist_id, video_ids, cache_dir) -> None`
- `add_to_cache(playlist_id, video_id, cache_dir) -> None`
- `remove_from_cache(playlist_id, video_id, cache_dir) -> None`

#### Commit
```
feat: プレイリスト動画IDキャッシュの実装（cache.py 新規追加）
```

---

### タスク 5: `process_add` キャッシュ対応

**変更ファイル:** `src/service/sync.py`, `src/tests/test_process.py`

#### Red
`tests/test_process.py` の `TestProcessAdd` に以下の5ケースを追加する（`test-cases.md` 参照）：
- `test_uses_cache_when_valid`
- `test_fetches_api_when_cache_miss`
- `test_saves_cache_after_api_fetch`
- `test_updates_cache_after_successful_add`
- `test_raises_quota_exceeded_on_fetch`
- `test_raises_quota_exceeded_on_insert`

既存テストも `cache_dir` 引数を受け取るように修正する（`tmp_path` を渡す）。

#### Green
`service/sync.py` の `process_add` を変更する：
- シグネチャに `cache_dir: Path` 引数を追加
- `fetch_playlist_video_ids` 呼び出し前に `load_playlist_cache` を試行
- キャッシュミス時のみ `fetch_playlist_video_ids` を呼び出し、結果を `save_playlist_cache` で保存
- `api_add_video` 成功後に `add_to_cache` を呼び出す
- `QuotaExceededError` はキャッチせず呼び出し元に伝播させる

#### Commit
```
feat: process_add にキャッシュ対応を追加
```

---

### タスク 6: `process_remove` キャッシュ対応

**変更ファイル:** `src/service/sync.py`, `src/tests/test_process.py`

#### Red
`tests/test_process.py` の `TestProcessRemove` に以下のケースを追加する：
- `test_updates_cache_after_successful_remove`

既存テストも `cache_dir` 引数を受け取るように修正する。

#### Green
`service/sync.py` の `process_remove` を変更する：
- シグネチャに `cache_dir: Path` 引数を追加
- `api_remove_video` 成功後に `remove_from_cache` を呼び出す

#### Commit
```
feat: process_remove 成功後にキャッシュから動画IDを削除
```

---

### タスク 7: `controller/cli.py` `QuotaExceededError` キャッチ

**変更ファイル:** `src/controller/cli.py`

#### 実装
`main()` に以下を追加する：
- `CACHE_DIR = Path("/data/youtube")` 定数を追加
- `process_add` / `process_remove` に `cache_dir=CACHE_DIR` を渡す
- `try/except QuotaExceededError` で `quota_reset_message()` を出力して `sys.exit(1)`

#### 確認方法
TDD対象外（CLIのE2Eテストは未整備のため）。
`make run` でコンテナ内で実行し、クォータ超過が発生した場合のメッセージを目視確認する。

#### Commit
```
feat: cli.py でクォータ超過を捕捉してリセット時刻を表示
```

---

### タスク 8: `docker-compose.yml` ボリュームマウント変更

**変更ファイル:** `docker-compose.yml`

#### 実装
ボリュームマウントをCSVファイル単体からディレクトリに変更する：

```yaml
# Before
- type: bind
  source: ../../footprints/youtube/playlist_history.csv
  target: /data/youtube/playlist_history.csv

# After
- type: bind
  source: ../../footprints/youtube
  target: /data/youtube
```

#### 確認方法
- `make down && make up` で再起動
- `make run` でコンテナが正常に起動し、CSVとキャッシュファイルが `/data/youtube/` に作成されることを確認

#### Commit
```
chore: docker-compose のボリュームマウントをディレクトリに変更
```

---

## 完了条件

- 全テストが通過していること（`pytest` でエラーなし）
- `make run` で正常に動作すること
- クォータ超過時にクラッシュせず、リセット時刻が表示されること
