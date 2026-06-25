# タスクリスト

TDDサイクル（Red → Green → Refactor → Commit）で進める。
各タスク完了後に `git commit` する。テストが通っていない状態でコミットしない。

---

## フェーズ0: 準備

- [x] 要件確定（壁打ち完了）
- [x] requirements.md 作成・承認
- [x] design.md 作成・承認
- [x] test-cases.md 作成・承認
- [x] polydock docker-python テンプレートをコピー
- [x] pyproject.toml を本プロジェクト用に更新
- [x] Makefile に `auth` / `run` ターゲット追加
- [x] .gitignore 更新（token.json, client_secret.json, csv, config.json）
- [x] README.md 作成
- [ ] `pytest-mock` を pyproject.toml dev-dependencies に追加
- [ ] `src/input/` ディレクトリ作成・空ファイル配置
- [ ] `git init` & 初回コミット

---

## フェーズ1: URL解析

**対象**: `extract_video_id(url)`

- [ ] `src/tests/test_video_id.py` にテストケース記述（test-cases.md §1 参照）
- [ ] テスト実行 → 全件 RED を確認
- [ ] `src/main.py` に `extract_video_id()` を実装
- [ ] テスト実行 → 全件 GREEN を確認
- [ ] `git commit`: `feat: extract_video_id の実装とテスト追加`

---

## フェーズ2: 入力ファイルパース

**対象**: `ParseResult`, `parse_input(path)`

- [ ] `src/tests/test_parse_input.py` にテストケース記述（test-cases.md §2 参照）
- [ ] テスト実行 → 全件 RED を確認
- [ ] `src/main.py` に `ParseResult` dataclass と `parse_input()` を実装（invalid_lines・duplicate_ids を収集）
- [ ] テスト実行 → 全件 GREEN を確認
- [ ] `git commit`: `feat: parse_input の実装とテスト追加（無効URL・重複を収集）`

---

## フェーズ3: CSV履歴管理

**対象**: `init_csv()`, `load_history()`, `append_history()`, `was_previously_added()`

- [ ] `src/tests/test_csv_history.py` にテストケース記述（test-cases.md §3 参照）
- [ ] テスト実行 → 全件 RED を確認
- [ ] `src/main.py` にCSV関連関数を実装
- [ ] テスト実行 → 全件 GREEN を確認
- [ ] `git commit`: `feat: CSV履歴管理の実装とテスト追加`

---

## フェーズ4: YouTube API操作

**対象**: `api_call_with_retry()`, `api_add_video()`, `api_remove_video()`

- [ ] `src/tests/test_api.py` にテストケース記述（test-cases.md §4〜6 参照）
- [ ] テスト実行 → 全件 RED を確認
- [ ] `src/main.py` にAPI関連関数を実装
- [ ] テスト実行 → 全件 GREEN を確認
- [ ] `git commit`: `feat: YouTube API操作の実装とテスト追加`

---

## フェーズ5: 処理フロー

**対象**: `AddResult`, `RemoveResult`, `process_add()`, `process_remove()`, `print_summary()`

- [ ] `src/tests/test_process.py` にテストケース記述（test-cases.md §7〜9 参照）
- [ ] テスト実行 → 全件 RED を確認
- [ ] `AddResult` / `RemoveResult` dataclass を実装
- [ ] `process_add()` を実装（CSV既存時の1件ずつ確認・409収集・APIエラー収集）
- [ ] `process_remove()` を実装（不在動画収集・APIエラー収集）
- [ ] `print_summary()` を実装（⚠️セクションが空なら非表示）
- [ ] テスト実行 → 全件 GREEN を確認
- [ ] `git commit`: `feat: 追加・削除処理フローの実装とテスト追加（取りこぼしゼロ設計）`

---

## フェーズ6: 認証・プレイリスト選択・エントリーポイント

**対象**: `build_youtube_client()`, `choose_playlists()`, `main()`

（認証とUI選択はモックが複雑なため統合テストレベルで確認）

- [ ] `build_youtube_client()` を実装（token.json読込・OAuth2フロー）
- [ ] `fetch_playlists()` / `choose_playlists()` を実装（questionary統合）
- [ ] `main()` を実装（全フローの結合）
- [ ] `make build` でDockerイメージビルド確認
- [ ] `git commit`: `feat: 認証・プレイリスト選択・エントリーポイントの実装`

---

## フェーズ7: 結合確認

- [ ] `make auth` で初回認証確認
- [ ] `make run` で実際のプレイリスト選択・追加・削除を確認
- [ ] `playlist_history.csv` に正しく記録されていることを確認
- [ ] `git commit`: `chore: 結合確認完了`

---

## ユーザー作業（残タスク）

- [ ] Google Cloud Console でOAuth2クライアント設定（詳細はREADME参照）
- [ ] `src/client_secret.json` を配置
- [ ] `make build` でイメージビルド
- [ ] `make auth` で初回認証 → `src/token.json` 生成
- [ ] `src/input/add.txt` にURLを貼り付けて `make run` で動作確認
