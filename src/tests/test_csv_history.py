import csv
import pytest
from pathlib import Path
from repository.history import CSV_HEADERS, init_csv, load_history, append_history, was_previously_added


class TestInitCsv:
    def test_creates_file_with_headers(self, tmp_path):
        p = tmp_path / "history.csv"
        init_csv(p)
        assert p.exists()
        with p.open() as f:
            assert csv.DictReader(f).fieldnames == CSV_HEADERS

    def test_does_not_overwrite_existing(self, tmp_path):
        p = tmp_path / "history.csv"
        p.write_text("existing content\n")
        init_csv(p)
        assert p.read_text() == "existing content\n"


class TestLoadHistory:
    def test_returns_records(self, tmp_path):
        p = tmp_path / "history.csv"
        init_csv(p)
        append_history("AAAAAAAAAAa", "タイトル", "https://youtu.be/AAAAAAAAAAa", "add", "PL1", p)
        history = load_history(p)
        assert len(history) == 1
        assert history[0]["video_id"] == "AAAAAAAAAAa"
        assert history[0]["action"] == "add"

    def test_empty_csv_returns_empty_list(self, tmp_path):
        p = tmp_path / "history.csv"
        init_csv(p)
        assert load_history(p) == []


class TestAppendHistory:
    def test_appends_all_fields(self, tmp_path):
        p = tmp_path / "history.csv"
        init_csv(p)
        append_history("AAAAAAAAAAa", "タイトル", "https://youtu.be/AAAAAAAAAAa", "add", "PL1", p)
        row = load_history(p)[0]
        assert row["video_id"] == "AAAAAAAAAAa"
        assert row["title"] == "タイトル"
        assert row["action"] == "add"
        assert row["playlist_id"] == "PL1"

    def test_title_can_be_empty(self, tmp_path):
        p = tmp_path / "history.csv"
        init_csv(p)
        append_history("AAAAAAAAAAa", "", "https://youtu.be/AAAAAAAAAAa", "add", "PL1", p)
        assert load_history(p)[0]["title"] == ""

    def test_multiple_appends(self, tmp_path):
        p = tmp_path / "history.csv"
        init_csv(p)
        append_history("AAAAAAAAAAa", "A", "url_a", "add", "PL1", p)
        append_history("BBBBBBBBBBb", "B", "url_b", "remove", "PL2", p)
        assert len(load_history(p)) == 2


class TestWasPreviouslyAdded:
    def test_returns_true_same_playlist(self):
        history = [{"video_id": "A", "playlist_id": "PL1", "action": "add"}]
        assert was_previously_added("A", history, "PL1") is True

    def test_returns_false_different_playlist(self):
        history = [{"video_id": "A", "playlist_id": "PL1", "action": "add"}]
        assert was_previously_added("A", history, "PL2") is False

    def test_returns_false_for_remove_action(self):
        history = [{"video_id": "A", "playlist_id": "PL1", "action": "remove"}]
        assert was_previously_added("A", history, "PL1") is False

    def test_returns_false_empty_history(self):
        assert was_previously_added("A", [], "PL1") is False
