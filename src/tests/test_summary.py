import pytest
from domain.models import ParseResult, AddResult, RemoveResult
from service.sync import print_summary


class TestPrintSummary:
    # ── 正常系 ────────────────────────────────────────────────────────────────

    def test_all_success_shows_counts(self, capsys):
        print_summary(ParseResult(), ParseResult(), AddResult(ok=3), RemoveResult(ok=2))
        out = capsys.readouterr().out
        assert "3" in out
        assert "2" in out

    def test_all_success_no_warning_section(self, capsys):
        print_summary(ParseResult(), ParseResult(), AddResult(ok=1), RemoveResult(ok=1))
        out = capsys.readouterr().out
        assert "⚠" not in out  # ⚠️ が出ない

    # ── 準正常系 ──────────────────────────────────────────────────────────────

    def test_invalid_urls_shown(self, capsys):
        parse_add = ParseResult(invalid_lines=["https://example.com/bad"])
        print_summary(parse_add, ParseResult(), AddResult(), RemoveResult())
        out = capsys.readouterr().out
        assert "https://example.com/bad" in out

    def test_duplicate_ids_shown(self, capsys):
        parse_add = ParseResult(duplicate_ids=["AAAAAAAAAAa"])
        print_summary(parse_add, ParseResult(), AddResult(), RemoveResult())
        out = capsys.readouterr().out
        assert "AAAAAAAAAAa" in out

    def test_already_in_playlist_shown(self, capsys):
        add_result = AddResult(already_in_playlist=[("AAAAAAAAAAa", "動画A")])
        print_summary(ParseResult(), ParseResult(), add_result, RemoveResult())
        out = capsys.readouterr().out
        assert "動画A" in out

    def test_not_found_shown(self, capsys):
        remove_result = RemoveResult(not_found=[("AAAAAAAAAAa", "動画A")])
        print_summary(ParseResult(), ParseResult(), AddResult(), remove_result)
        out = capsys.readouterr().out
        assert "動画A" in out

    def test_api_errors_shown(self, capsys):
        add_result = AddResult(api_errors=[("AAAAAAAAAAa", "動画A", "HTTP 500")])
        print_summary(ParseResult(), ParseResult(), add_result, RemoveResult())
        out = capsys.readouterr().out
        assert "動画A" in out

    def test_multiple_warning_categories_all_shown(self, capsys):
        parse_add = ParseResult(invalid_lines=["bad_url"], duplicate_ids=["vid1"])
        add_result = AddResult(already_in_playlist=[("vid2", "動画B")])
        remove_result = RemoveResult(not_found=[("vid3", "動画C")])
        print_summary(parse_add, ParseResult(), add_result, remove_result)
        out = capsys.readouterr().out
        assert "bad_url" in out
        assert "vid1" in out
        assert "動画B" in out
        assert "動画C" in out
