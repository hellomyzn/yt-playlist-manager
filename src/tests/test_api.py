import pytest
from freezegun import freeze_time
from unittest.mock import MagicMock, patch
from googleapiclient.errors import HttpError
from repository.youtube import QuotaExceededError, api_call_with_retry, api_add_video, api_remove_video, fetch_playlist_video_ids, quota_reset_message


def make_http_error(status: int, reason: str = "") -> HttpError:
    resp = MagicMock()
    resp.status = status
    content = f'{{"error":{{"errors":[{{"reason":"{reason}"}}]}}}}'.encode()
    return HttpError(resp=resp, content=content)


class TestApiCallWithRetry:
    def test_returns_result_on_success(self):
        fn = MagicMock(return_value="ok")
        assert api_call_with_retry(fn) == "ok"
        fn.assert_called_once()

    def test_raises_quota_exceeded_error_on_quota_exceeded(self):
        fn = MagicMock(side_effect=make_http_error(403, "quotaExceeded"))
        with pytest.raises(QuotaExceededError):
            api_call_with_retry(fn)

    def test_reraises_non_quota_403(self):
        fn = MagicMock(side_effect=make_http_error(403, "forbidden"))
        with pytest.raises(HttpError):
            api_call_with_retry(fn)

    def test_reraises_404(self):
        fn = MagicMock(side_effect=make_http_error(404))
        with pytest.raises(HttpError):
            api_call_with_retry(fn)

    def test_reraises_500(self):
        fn = MagicMock(side_effect=make_http_error(500))
        with pytest.raises(HttpError):
            api_call_with_retry(fn)


class TestQuotaResetMessage:
    def test_returns_string_containing_key_phrases(self):
        msg = quota_reset_message()
        assert isinstance(msg, str)
        assert "クォータ" in msg
        assert "太平洋時間" in msg

    @freeze_time("2026-06-26T10:00:00+00:00")
    def test_returns_correct_remaining_hours(self):
        # PT = UTC-7 (PDT): 10:00 UTC = 03:00 PDT → 次の PT 0:00 まで 21 時間
        msg = quota_reset_message()
        assert "21時間" in msg


class TestFetchPlaylistVideoIds:
    def test_raises_quota_exceeded_when_list_fails(self):
        yt = MagicMock()
        resp = MagicMock()
        resp.status = 403
        yt.playlistItems().list().execute.side_effect = HttpError(
            resp=resp,
            content=b'{"error":{"errors":[{"reason":"quotaExceeded"}]}}',
        )
        with pytest.raises(QuotaExceededError):
            fetch_playlist_video_ids(yt, "PL1")


class TestApiAddVideo:
    def test_returns_true_on_success(self):
        yt = MagicMock()
        yt.playlistItems().insert().execute.return_value = {}
        assert api_add_video(yt, "PL1", "AAAAAAAAAAa") is True

    def test_returns_false_on_409(self):
        yt = MagicMock()
        yt.playlistItems().insert().execute.side_effect = make_http_error(409)
        assert api_add_video(yt, "PL1", "AAAAAAAAAAa") is False

    def test_reraises_on_500(self):
        yt = MagicMock()
        yt.playlistItems().insert().execute.side_effect = make_http_error(500)
        with pytest.raises(HttpError):
            api_add_video(yt, "PL1", "AAAAAAAAAAa")


class TestApiRemoveVideo:
    def test_returns_true_on_success(self):
        yt = MagicMock()
        yt.playlistItems().list().execute.return_value = {"items": [{"id": "item_001"}]}
        yt.playlistItems().delete().execute.return_value = {}
        assert api_remove_video(yt, "PL1", "AAAAAAAAAAa") is True

    def test_returns_false_when_not_in_playlist(self):
        yt = MagicMock()
        yt.playlistItems().list().execute.return_value = {"items": []}
        assert api_remove_video(yt, "PL1", "AAAAAAAAAAa") is False

    def test_reraises_on_list_error(self):
        yt = MagicMock()
        yt.playlistItems().list().execute.side_effect = make_http_error(500)
        with pytest.raises(HttpError):
            api_remove_video(yt, "PL1", "AAAAAAAAAAa")

    def test_reraises_on_delete_error(self):
        yt = MagicMock()
        yt.playlistItems().list().execute.return_value = {"items": [{"id": "item_001"}]}
        yt.playlistItems().delete().execute.side_effect = make_http_error(500)
        with pytest.raises(HttpError):
            api_remove_video(yt, "PL1", "AAAAAAAAAAa")
