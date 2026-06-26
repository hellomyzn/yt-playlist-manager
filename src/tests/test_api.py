import pytest
from unittest.mock import MagicMock, patch
from googleapiclient.errors import HttpError
from repository.youtube import QuotaExceededError, api_call_with_retry, api_add_video, api_remove_video


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
