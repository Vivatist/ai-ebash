import pytest
from unittest.mock import patch
from requests.exceptions import HTTPError
from aiebash.openai_client import OpenAIClient

def test_send_chat_raises_connection_error():
    client = OpenAIClient(model="gpt-3.5-turbo", api_url="https://any-url", api_key="fake-key")
    messages = [{"role": "user", "content": "test"}]
    error_msg = "HTTPSConnectionPool(host='openai-proxy.andrey-bch-1976.workers.dev', port=443): Max retries exceeded with url: /v1/chat/completions (Caused by NameResolutionError('<urllib3.connection.HTTPSConnection object at 0x7a8bdb82d3a0>: Failed to resolve 'openai-proxy.andrey-bch-1976.workers.dev' ([Errno -3] Temporary failure in name resolution)'))"
    from requests.exceptions import ConnectionError
    with patch("requests.post", side_effect=ConnectionError(error_msg)):
        with patch("builtins.print") as mock_print:
            with pytest.raises(ConnectionError) as exc_info:
                client._send_chat(messages)
            mock_print.assert_not_called()
    assert "Max retries exceeded" in str(exc_info.value)

def test_send_chat_raises_http_error_and_message_hidden():
    client = OpenAIClient(model="gpt-3.5-turbo", api_url="https://fake-url", api_key="fake-key")
    messages = [{"role": "user", "content": "test"}]
    error_msg = "403 Client Error: Forbidden for url: https://any-url"
    with patch("requests.post", side_effect=HTTPError(error_msg)):
        with patch("builtins.print") as mock_print:
            with pytest.raises(HTTPError) as exc_info:
                client._send_chat(messages)
            mock_print.assert_not_called()
    assert "403 Client Error: Forbidden" in str(exc_info.value)
