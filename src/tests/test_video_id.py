import pytest
from domain.parser import extract_video_id


class TestExtractVideoId:
    # ── 正常系 ────────────────────────────────────────────────────────────────

    def test_watch_url(self):
        assert extract_video_id("https://www.youtube.com/watch?v=dQw4w9WgXcY") == "dQw4w9WgXcY"

    def test_youtu_be_url(self):
        assert extract_video_id("https://youtu.be/dQw4w9WgXcY") == "dQw4w9WgXcY"

    def test_shorts_url(self):
        assert extract_video_id("https://www.youtube.com/shorts/dQw4w9WgXcY") == "dQw4w9WgXcY"

    def test_embed_url(self):
        assert extract_video_id("https://www.youtube.com/embed/dQw4w9WgXcY") == "dQw4w9WgXcY"

    def test_http_scheme(self):
        assert extract_video_id("http://youtu.be/dQw4w9WgXcY") == "dQw4w9WgXcY"

    def test_mobile_url(self):
        assert extract_video_id("https://m.youtube.com/watch?v=dQw4w9WgXcY") == "dQw4w9WgXcY"

    # ── 準正常系 ──────────────────────────────────────────────────────────────

    def test_extra_params_after_v(self):
        assert extract_video_id("https://youtube.com/watch?v=dQw4w9WgXcY&t=120s") == "dQw4w9WgXcY"

    def test_v_param_not_first(self):
        assert extract_video_id("https://youtube.com/watch?feature=share&v=dQw4w9WgXcY") == "dQw4w9WgXcY"

    def test_leading_trailing_spaces(self):
        assert extract_video_id("  https://youtu.be/dQw4w9WgXcY  ") == "dQw4w9WgXcY"

    # ── 異常系 ────────────────────────────────────────────────────────────────

    def test_non_youtube_domain(self):
        assert extract_video_id("https://example.com/watch?v=dQw4w9WgXcY") is None

    def test_watch_url_no_v_param(self):
        assert extract_video_id("https://www.youtube.com/watch") is None

    def test_invalid_video_id_length(self):
        assert extract_video_id("https://www.youtube.com/watch?v=SHORT") is None

    def test_not_a_url(self):
        assert extract_video_id("not a url") is None

    def test_empty_string(self):
        assert extract_video_id("") is None
