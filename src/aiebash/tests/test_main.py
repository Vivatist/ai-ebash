
import sys
from pathlib import Path
import pytest
from unittest.mock import patch
from requests.exceptions import HTTPError
import importlib.util

# Импортируем src/aiebash/__main__.py как модуль
MAIN_PATH = Path(__file__).resolve().parents[0] / ".." / "__main__.py"
spec = importlib.util.spec_from_file_location("main_mod", str(MAIN_PATH.resolve()))
main_mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(main_mod)


def test_main_handles_http_error(monkeypatch):
    # Мокаем аргументы командной строки
    monkeypatch.setattr(main_mod, "parse_args", lambda: type("Args", (), {"run": False, "chat": False, "prompt": ["тест"]})())
    # Мокаем llm_client.send_prompt для выбрасывания HTTPError
    with patch.object(main_mod.llm_client, "send_prompt", side_effect=HTTPError("403 Client Error")):
        # Мокаем Console.print для отслеживания вывода
        with patch.object(main_mod.Console, "print") as mock_print:
            # main() не должен падать, просто завершиться
            main_mod.main()
            mock_print.assert_not_called()
            
def test_main_handles_connection_error(monkeypatch):
    import requests
    # Мокаем аргументы командной строки
    monkeypatch.setattr(main_mod, "parse_args", lambda: type("Args", (), {"run": False, "chat": False, "prompt": ["тест"]})())
    # Мокаем llm_client.send_prompt для выбрасывания ConnectionError
    with patch.object(main_mod.llm_client, "send_prompt", side_effect=requests.exceptions.ConnectionError("Max retries exceeded")):
        with patch.object(main_mod.Console, "print") as mock_print:
            # main() не должен падать, просто завершиться
            main_mod.main()
            mock_print.assert_not_called()