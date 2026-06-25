import pytest
from pathlib import Path
from domain.parser import parse_input
from domain.models import ParseResult


class TestParseInput:
    # ── 正常系 ────────────────────────────────────────────────────────────────

    def test_url_with_title(self, tmp_path):
        f = tmp_path / "add.txt"
        f.write_text("https://youtu.be/AAAAAAAAAAa | 動画タイトル\n")
        result = parse_input(f)
        assert isinstance(result, ParseResult)
        assert result.items == [("AAAAAAAAAAa", "動画タイトル", "https://youtu.be/AAAAAAAAAAa")]
        assert result.invalid_lines == []
        assert result.duplicate_ids == []

    def test_url_without_title(self, tmp_path):
        f = tmp_path / "add.txt"
        f.write_text("https://youtu.be/AAAAAAAAAAa\n")
        result = parse_input(f)
        assert result.items == [("AAAAAAAAAAa", "", "https://youtu.be/AAAAAAAAAAa")]

    def test_multiple_valid_lines(self, tmp_path):
        f = tmp_path / "add.txt"
        f.write_text(
            "https://youtu.be/AAAAAAAAAAa | 動画A\n"
            "https://youtu.be/BBBBBBBBBBb | 動画B\n"
            "https://youtu.be/CCCCCCCCCCc | 動画C\n"
        )
        result = parse_input(f)
        assert len(result.items) == 3
        assert result.invalid_lines == []
        assert result.duplicate_ids == []

    # ── 準正常系 ──────────────────────────────────────────────────────────────

    def test_empty_lines_skipped(self, tmp_path):
        f = tmp_path / "add.txt"
        f.write_text("https://youtu.be/AAAAAAAAAAa | 動画A\n\n\nhttps://youtu.be/BBBBBBBBBBb | 動画B\n")
        result = parse_input(f)
        assert len(result.items) == 2
        assert result.invalid_lines == []

    def test_duplicate_video_id_first_wins(self, tmp_path):
        f = tmp_path / "add.txt"
        f.write_text(
            "https://youtu.be/AAAAAAAAAAa | 動画A\n"
            "https://youtu.be/AAAAAAAAAAa | 動画A重複\n"
        )
        result = parse_input(f)
        assert len(result.items) == 1
        assert result.items[0][1] == "動画A"
        assert "AAAAAAAAAAa" in result.duplicate_ids

    def test_mix_valid_and_invalid(self, tmp_path):
        f = tmp_path / "add.txt"
        f.write_text(
            "https://youtu.be/AAAAAAAAAAa | 有効\n"
            "https://example.com/invalid | 無効\n"
        )
        result = parse_input(f)
        assert len(result.items) == 1
        assert len(result.invalid_lines) == 1
        assert "https://example.com/invalid" in result.invalid_lines[0]

    def test_all_empty_lines(self, tmp_path):
        f = tmp_path / "add.txt"
        f.write_text("\n\n\n")
        result = parse_input(f)
        assert result.items == []
        assert result.invalid_lines == []
        assert result.duplicate_ids == []

    # ── 異常系 ────────────────────────────────────────────────────────────────

    def test_file_not_found(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            parse_input(tmp_path / "nonexistent.txt")

    def test_all_invalid_urls(self, tmp_path):
        f = tmp_path / "add.txt"
        f.write_text(
            "https://example.com/a\n"
            "https://example.com/b\n"
        )
        result = parse_input(f)
        assert result.items == []
        assert len(result.invalid_lines) == 2
