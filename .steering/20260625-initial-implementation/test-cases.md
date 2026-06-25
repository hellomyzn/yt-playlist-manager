# テストケース一覧

実装前にテストケースの妥当性を確認するためのドキュメント。
各機能について正常系・準正常系・異常系を網羅する。

---

## 1. `extract_video_id(url: str) -> str | None`

YouTube URLから video_id（11文字）を抽出する。

### 正常系

| # | 入力 | 期待値 |
|---|---|---|
| N-1 | `https://www.youtube.com/watch?v=dQw4w9WgXcY` | `dQw4w9WgXcY` |
| N-2 | `https://youtu.be/dQw4w9WgXcY` | `dQw4w9WgXcY` |
| N-3 | `https://www.youtube.com/shorts/dQw4w9WgXcY` | `dQw4w9WgXcY` |
| N-4 | `https://www.youtube.com/embed/dQw4w9WgXcY` | `dQw4w9WgXcY` |
| N-5 | `http://youtu.be/dQw4w9WgXcY` | `dQw4w9WgXcY` （http）|
| N-6 | `https://m.youtube.com/watch?v=dQw4w9WgXcY` | `dQw4w9WgXcY` （モバイル）|

### 準正常系

| # | 入力 | 期待値 | 理由 |
|---|---|---|---|
| Q-1 | `https://youtube.com/watch?v=dQw4w9WgXcY&t=120s` | `dQw4w9WgXcY` | 追加パラメータあり |
| Q-2 | `https://youtube.com/watch?feature=share&v=dQw4w9WgXcY` | `dQw4w9WgXcY` | vパラメータが2番目 |
| Q-3 | `  https://youtu.be/dQw4w9WgXcY  ` | `dQw4w9WgXcY` | 前後スペース |

### 異常系

| # | 入力 | 期待値 | 理由 |
|---|---|---|---|
| E-1 | `https://example.com/watch?v=dQw4w9WgXcY` | `None` | YouTube以外のドメイン |
| E-2 | `https://www.youtube.com/watch` | `None` | vパラメータなし |
| E-3 | `https://www.youtube.com/watch?v=SHORT` | `None` | 11文字未満のvideo_id |
| E-4 | `not a url` | `None` | URL形式でない |
| E-5 | `""` | `None` | 空文字 |

---

## 2. `parse_input(path: Path) -> ParseResult`

入力ファイルを読み込み、有効アイテムと各種非正常ケースを分けて返す。

```python
@dataclass
class ParseResult:
    items: list[tuple[str, str, str]]  # (video_id, title, url)
    invalid_lines: list[str]           # video_id抽出失敗した元の行
    duplicate_ids: list[str]           # 重複していたvideo_id
```

### 正常系

| # | 入力ファイル内容 | items | invalid_lines | duplicate_ids |
|---|---|---|---|---|
| N-1 | `https://youtu.be/AAAAAAAAAAa \| 動画タイトル` | 1件 | `[]` | `[]` |
| N-2 | タイトルなし: `https://youtu.be/AAAAAAAAAAa` | 1件（title=""） | `[]` | `[]` |
| N-3 | 有効な行が3行 | 3件 | `[]` | `[]` |

### 準正常系

| # | 入力ファイル内容 | items | invalid_lines | duplicate_ids | 理由 |
|---|---|---|---|---|---|
| Q-1 | 空行を含む | 空行を除いた件数 | `[]` | `[]` | 空行は無視 |
| Q-2 | 同じvideo_idが2行 | 1件（先勝ち） | `[]` | `["AAAAAAAAAAa"]` | 重複記録 |
| Q-3 | 有効1行 + 無効1行 | 1件 | 無効行の文字列 | `[]` | 無効記録 |
| Q-4 | 全行が空行 | `[]` | `[]` | `[]` | 空ファイル相当 |

### 異常系

| # | 入力 | 期待値 | 理由 |
|---|---|---|---|
| E-1 | ファイルが存在しない | `FileNotFoundError` が発生 | 呼び出し元でハンドリング |
| E-2 | 全行が無効URL | items=`[]`, invalid_lines=全行 | すべて記録 |

---

## 3. `was_previously_added(video_id, history, playlist_id) -> bool`

指定の `video_id` が同じ `playlist_id` に追加済みかCSV履歴から判定する。

### 正常系

| # | 履歴 | video_id | playlist_id | 期待値 |
|---|---|---|---|---|
| N-1 | `[{video_id: "A", playlist_id: "PL1", action: "add"}]` | `"A"` | `"PL1"` | `True` |

### 準正常系

| # | 状況 | 期待値 | 理由 |
|---|---|---|---|
| Q-1 | 同video_idだが別playlist_id | `False` | プレイリストが違う |
| Q-2 | 同video_idでaction=remove | `False` | 削除済みは「追加済み」ではない |
| Q-3 | 履歴が空 | `False` | 初回実行 |

---

## 4. `api_call_with_retry(fn)`

API呼び出しをラップし、Quota超過時はポーリングで再試行する。

### 正常系

| # | fnの挙動 | 期待値 |
|---|---|---|
| N-1 | 初回で成功 | fnの戻り値を返す |

### 準正常系

| # | fnの挙動 | 期待値 | 理由 |
|---|---|---|---|
| Q-1 | 1回目 403 quotaExceeded → 2回目成功 | 2回目の戻り値 | ポーリング後リトライ |

### 異常系

| # | fnの挙動 | 期待値 | 理由 |
|---|---|---|---|
| E-1 | 403（quotaExceeded以外） | `HttpError` を再raise | quota以外は即失敗 |
| E-2 | 404 | `HttpError` を再raise | リトライしない |
| E-3 | 500 | `HttpError` を再raise | リトライしない |

---

## 5. `api_add_video(youtube, playlist_id, video_id) -> bool`

プレイリストに動画を追加する。

### 正常系

| # | APIの挙動 | 期待値 |
|---|---|---|
| N-1 | 追加成功（200） | `True` |

### 準正常系

| # | APIの挙動 | 期待値 | 理由 |
|---|---|---|---|
| Q-1 | 409 Conflict（すでに存在） | `False` + WARNログ出力 | 重複追加はスキップ |

### 異常系

| # | APIの挙動 | 期待値 | 理由 |
|---|---|---|---|
| E-1 | 500 Server Error | `False` + ERRORログ出力 | クラッシュしない |
| E-2 | 403（quota以外） | `False` + ERRORログ出力 | クラッシュしない |

---

## 6. `api_remove_video(youtube, playlist_id, video_id) -> bool`

プレイリストから動画を削除する。内部で `_get_playlist_item_id()` を呼ぶ。

### 正常系

| # | 状況 | 期待値 |
|---|---|---|
| N-1 | 動画が存在し削除成功 | `True` |

### 準正常系

| # | 状況 | 期待値 | 理由 |
|---|---|---|---|
| Q-1 | プレイリストに動画が存在しない（item_id が None） | `False` + WARNログ | 存在しない削除はスキップ |

### 異常系

| # | 状況 | 期待値 | 理由 |
|---|---|---|---|
| E-1 | `playlistItems.list` でHTTPError | `False` + ERRORログ | クラッシュしない |
| E-2 | `playlistItems.delete` でHTTPError | `False` + ERRORログ | クラッシュしない |

---

## 7. `process_add(youtube, playlist, history) -> AddResult`

`add.txt` を処理してプレイリストに追加する。

```python
@dataclass
class AddResult:
    ok: int
    confirmed_skip: int          # ユーザーが再追加をN選択
    already_in_playlist: list[tuple[str, str]]  # (video_id, title) 409ケース
    api_errors: list[tuple[str, str, str]]       # (video_id, title, error_msg)
```

### 正常系

| # | 状況 | 期待値 |
|---|---|---|
| N-1 | add.txt に有効URL 3件、全追加成功 | `ok=3`, 他すべて空 |
| N-2 | CSV履歴に既存あり → ユーザーが `y` を選択 | 追加される・`ok` にカウント |
| N-3 | CSV履歴に既存あり → ユーザーが `N` を選択 | スキップ・`confirmed_skip` にカウント |

### 準正常系

| # | 状況 | 期待値 | 理由 |
|---|---|---|---|
| Q-1 | add.txt が空または存在しない | 全フィールド0/空 | スキップ |
| Q-2 | 1件が409（プレイリスト既存だがCSV未記録） | `already_in_playlist` に記録 | 不整合として報告 |
| Q-3 | 有効2件成功 + 1件409 | `ok=2`, `already_in_playlist` 1件 | |

### 異常系

| # | 状況 | 期待値 | 理由 |
|---|---|---|---|
| E-1 | APIエラー（500）が1件で発生 | `api_errors` に記録 | クラッシュしない |

---

## 8. `process_remove(youtube, playlist) -> RemoveResult`

`remove.txt` を処理してプレイリストから削除する。

```python
@dataclass
class RemoveResult:
    ok: int
    not_found: list[tuple[str, str]]     # (video_id, title) プレイリストに不在
    api_errors: list[tuple[str, str, str]]  # (video_id, title, error_msg)
```

### 正常系

| # | 状況 | 期待値 |
|---|---|---|
| N-1 | remove.txt に有効URL 2件、全削除成功 | `ok=2`, 他すべて空 |

### 準正常系

| # | 状況 | 期待値 | 理由 |
|---|---|---|---|
| Q-1 | remove.txt が空または存在しない | 全フィールド0/空 | スキップ |
| Q-2 | 1件がプレイリストに不在 | `not_found` に記録 | 報告対象 |
| Q-3 | 有効1件成功 + 1件不在 | `ok=1`, `not_found` 1件 | |

### 異常系

| # | 状況 | 期待値 | 理由 |
|---|---|---|---|
| E-1 | APIエラー（500）が1件で発生 | `api_errors` に記録 | クラッシュしない |

---

## 9. `print_summary(parse_add, parse_remove, add_result, remove_result)`

完了後サマリーを表示する。

### 正常系

| # | 状況 | 期待値 |
|---|---|---|
| N-1 | 全件正常処理 | ✅ 成功件数のみ表示。⚠️セクションなし |

### 準正常系

| # | 状況 | 期待値 |
|---|---|---|
| Q-1 | 無効URLあり | ⚠️ セクションに無効URL一覧が表示される |
| Q-2 | 重複スキップあり | ⚠️ セクションに重複video_id一覧が表示される |
| Q-3 | 409あり | ⚠️ セクションに既存動画一覧が表示される |
| Q-4 | 削除対象不在あり | ⚠️ セクションに不在動画一覧が表示される |
| Q-5 | APIエラーあり | ⚠️ セクションにエラー動画一覧が表示される |
| Q-6 | 複数カテゴリ混在 | 該当するカテゴリがすべて表示される |

---

## テスト実装方針

### 使用ライブラリ
- `pytest` - テストフレームワーク
- `pytest-mock` - モック（追加）
- `unittest.mock.MagicMock` - YouTube APIクライアントのモック

### フィクスチャ設計
```python
@pytest.fixture
def tmp_add_file(tmp_path):
    f = tmp_path / "add.txt"
    f.write_text("https://youtu.be/AAAAAAAAAAa | テスト動画\n")
    return f

@pytest.fixture
def mock_youtube():
    return MagicMock()

@pytest.fixture
def sample_history():
    return [
        {"video_id": "AAAAAAAAAAa", "playlist_id": "PL1", "action": "add"},
    ]
```

### モック対象
- `youtube.playlistItems().insert().execute()` - 追加API
- `youtube.playlistItems().list().execute()` - 検索API
- `youtube.playlistItems().delete().execute()` - 削除API
- `youtube.playlists().list().execute()` - プレイリスト一覧API
- `time.sleep` - 待機処理（テスト高速化のため）
