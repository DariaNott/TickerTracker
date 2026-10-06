from unittest import mock

from alerts import services


def test_returns_false_when_token_missing():
    with mock.patch.object(services, "TELEGRAM_BOT_TOKEN", None):
        ok = services.send_telegram_notification(chat_id="12345", message="Hi")
        assert ok is False


def test_returns_false_when_chat_id_missing():
    with mock.patch.object(services, "TELEGRAM_BOT_TOKEN", "123:abc"):
        ok = services.send_telegram_notification(chat_id="", message="Hi")
        assert ok is False


def test_success_request_and_true_returned():
    with mock.patch.object(services, "TELEGRAM_BOT_TOKEN", "123:abc"):
        fake_response = mock.Mock()
        fake_response.raise_for_status.return_value = None

        with mock.patch("alerts.services.requests.post", return_value=fake_response) as mpost:
            ok = services.send_telegram_notification(chat_id="777", message="Hello!")
            assert ok is True
            expected_url = "https://api.telegram.org/bot123:abc/sendMessage"
            mpost.assert_called_once()
            args, kwargs = mpost.call_args
            assert args[0] == expected_url
            assert "json" in kwargs
            assert kwargs["json"]["chat_id"] == "777"
            assert kwargs["json"]["text"] == "Hello!"