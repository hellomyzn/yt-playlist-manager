# 開発ガイドライン

## コーディング規約

### 言語・スタイル

- Python 3.11+ の型ヒントを使用する（`str | None`, `list[dict]` など）
- PEP 8 に準拠する
- 1行の最大文字数は88文字（Black互換）
- f-string を優先する（`%` 形式・`.format()` は使わない）

### 命名規則

| 対象 | 規則 | 例 |
|---|---|---|
| 変数・関数 | snake_case | `video_id`, `parse_input` |
| クラス | PascalCase | `ParseResult`, `AddResult` |
| 定数 | UPPER_SNAKE_CASE | `QUOTA_WAIT`, `CSV_HEADERS` |
| プライベート関数 | `_` プレフィックス | `_interval()`, `_get_playlist_item_id()` |
| モジュール | snake_case | `cli.py`, `sync.py` |

### コメント・ドキュメント

- コメントは「なぜ」を書く。「何をしている」はコードが語る
- 1行コメントのみ許可（複数行コメントブロックは原則不要）
- 関数のdocstringは副作用・戻り値が非自明な場合のみ書く

### インポート

- 標準ライブラリ → サードパーティ → ローカルの順に、グループ間は空行で区切る
- ワイルドカードインポート（`from x import *`）は禁止

---

## テスト規約

### フレームワーク

- `pytest` を使用する
- テストファイルは `src/tests/test_*.py` に配置する
- `pytest-mock` を使用し、`unittest.mock` は直接使わない

### 外部依存のモック方針

| 依存 | 方針 |
|---|---|
| YouTube API クライアント | `mocker.MagicMock()` でモック化 |
| ファイルI/O | `tmp_path` フィクスチャで実ファイルを使用 |
| 時刻 | `freezegun` または `monkeypatch` で固定 |
| stdin（questionary） | `mocker.patch("questionary.confirm")` でモック化 |

### テストの分類と網羅基準

| 種別 | 定義 |
|---|---|
| 正常系 | 想定入力で期待出力が得られる |
| 準正常系 | 境界値・エッジケースでも仕様通りに動く |
| 異常系 | 不正入力・外部障害でクラッシュしない |

機能単位で正常系・準正常系・異常系をすべて定義する。

### TDDサイクル

```
test-cases.md で定義（承認後）
    → テストコードを書く（Red）
    → 最小限の実装（Green）
    → リファクタリング（Refactor）
    → git commit
```

**実装コードより先にテストコードを書く。** テストが通っていない状態でのコミットは禁止。

---

## Git規約

### コミット粒度

- タスクリストの各タスク完了後に1コミット
- テストがすべてPASSしている状態でのみコミット
- `--no-verify` は絶対に使わない

### コミットメッセージ

```
<プレフィックス>: <内容（日本語）>
```

| プレフィックス | 用途 |
|---|---|
| `feat` | 新機能の追加 |
| `fix` | バグ修正 |
| `refactor` | リファクタリング（振る舞い変更なし） |
| `test` | テストのみの変更 |
| `docs` | ドキュメントのみの変更 |
| `chore` | ビルド・設定・依存関係の変更 |

例:
```
feat: extract_video_id の実装とテスト追加
feat: parse_input の実装とテスト追加（重複除去対応）
feat: CSV履歴管理の実装とテスト追加
fix: 409 Conflict のハンドリングを修正
```

### ブランチ運用

- `main` ブランチが常にデプロイ可能な状態を維持する
- 機能開発は `feat/[タイトル]` ブランチで行う（任意）

---

## 品質チェック

コード変更後は必ず以下を確認する:

```bash
# テスト実行
make test

# カバレッジ確認（任意）
make coverage
```

---

## 開発環境セットアップ

```bash
# 1. 依存関係のビルド
make build

# 2. Google Cloud Console で OAuth2 クライアントIDを作成し、
#    src/client_secret.json に配置

# 3. 初回認証
make auth

# 4. 実行
make run
```

### 環境変数

| 変数 | デフォルト | 説明 |
|---|---|---|
| `INTERVAL_SECONDS` | `1.0` | API リクエスト間の待機秒数 |

---

## セキュリティ

- `client_secret.json`・`token.json` は `.gitignore` に登録し、絶対にコミットしない
- `input/add.txt`・`input/remove.txt` はURLのみを含むため機密情報は不要
- 入力URLは `extract_video_id()` でバリデーションしてから処理する
