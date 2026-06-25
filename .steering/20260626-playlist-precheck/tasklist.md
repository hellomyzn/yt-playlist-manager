# タスクリスト: プレイリスト事前チェック機能

TDDサイクル（Red → Green → Refactor → Commit）で進める。

---

## タスク1: `fetch_playlist_video_ids` の実装

### Red
- [ ] `tests/test_fetch_playlists.py` に `TestFetchPlaylistVideoIds` クラスを追加（test-cases.md §1 参照）
- [ ] テスト実行 → 全件 RED を確認（ImportError）

### Green
- [ ] `repository/youtube.py` に `fetch_playlist_video_ids` を実装（ページネーション対応）
- [ ] テスト実行 → 全件 GREEN を確認

### Commit
- [ ] `git commit`: `feat: fetch_playlist_video_ids の実装とテスト追加（ページネーション対応）`

---

## タスク2: `process_add` をAPIベース＋CSVベースの2段チェックに変更

### Red
- [ ] `tests/test_process.py` の `TestProcessAdd` を更新（test-cases.md §2 参照）
  - 全テストに `patch("service.sync.fetch_playlist_video_ids", return_value=set(...))` を追加
  - `test_previously_added_*` を `test_already_in_playlist_*` / CSV確認テストに置き換え
- [ ] テスト実行 → RED を確認（`fetch_playlist_video_ids` が `service.sync` から見えない）

### Green
- [ ] `service/sync.py` を更新
  - `fetch_playlist_video_ids` を import に追加
  - `process_add` の先頭で `fetch_playlist_video_ids(youtube, playlist["id"])` を呼ぶ
  - ① `existing_ids` に含まれる → `already_in_playlist` に追記してスキップ
  - ② `was_previously_added` で CSV確認 → ユーザー confirm（既存ロジック流用）
  - ③ どちらでもなければ追加
- [ ] テスト実行 → 全件 GREEN を確認（75件 → 78件）

### Commit
- [ ] `git commit`: `feat: process_add にAPIベース事前チェックを追加（プレイリスト既存は自動スキップ）`
