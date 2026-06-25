import json
import pytest
from pathlib import Path
from repository.config import load_config, save_config


class TestLoadConfig:
    def test_returns_empty_dict_when_missing(self, tmp_path):
        result = load_config(tmp_path / "config.json")
        assert result == {}

    def test_returns_saved_data(self, tmp_path):
        p = tmp_path / "config.json"
        p.write_text('{"last_add_playlist_id": "PL1"}')
        assert load_config(p)["last_add_playlist_id"] == "PL1"

    def test_returns_all_fields(self, tmp_path):
        p = tmp_path / "config.json"
        p.write_text('{"last_add_playlist_id": "PL1", "last_remove_playlist_id": "PL2"}')
        cfg = load_config(p)
        assert cfg["last_add_playlist_id"] == "PL1"
        assert cfg["last_remove_playlist_id"] == "PL2"


class TestSaveConfig:
    def test_creates_file(self, tmp_path):
        p = tmp_path / "config.json"
        save_config(p, {"last_add_playlist_id": "PL1"})
        assert p.exists()
        assert json.loads(p.read_text())["last_add_playlist_id"] == "PL1"

    def test_overwrites_existing(self, tmp_path):
        p = tmp_path / "config.json"
        p.write_text('{"last_add_playlist_id": "OLD"}')
        save_config(p, {"last_add_playlist_id": "NEW"})
        assert json.loads(p.read_text())["last_add_playlist_id"] == "NEW"

    def test_roundtrip(self, tmp_path):
        p = tmp_path / "config.json"
        data = {"last_add_playlist_id": "PL1", "last_remove_playlist_id": "PL2"}
        save_config(p, data)
        assert load_config(p) == data
