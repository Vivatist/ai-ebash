# Интеграционные тесты для ai.py (pytest)
import sys
import types
import importlib

import pytest


def _prepare_settings_module(tmp_settings=None):
    """
    Помещает модуль settings в sys.modules перед импортом ai, затем импортирует ai заново.
    """
    sys.modules.pop("ai", None)
    settings = types.ModuleType("settings")
    settings.API_URL = "http://example.test/api"
    settings.MODEL = "test-model"
    settings.CONTEXT = "CTX: $(lsb_release -ds), $SHELL, $HOME"
    settings.EXTRA_CONTEXT = ["extra1"]
    if tmp_settings:
        for k, v in tmp_settings.items():
            setattr(settings, k, v)
    sys.modules["settings"] = settings
    return importlib.import_module("ai")


def test_cli_prints_formatted_answer(monkeypatch, capsys):
    ai = _prepare_settings_module()

    # Подменяем контекст, чтобы не вызывать lsb_release
    monkeypatch.setattr(ai, "get_system_context", lambda: "SYS_CTX")

    # Формируем ответ ассистента с разными маркерами (код, inline, bold, ###)
    assistant_content = (
        "Перед **жирно** и `inline` ### заметка ### ```bash\n"
        "echo hi\n"
        "``` после"
    )

    class FakeResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return {"choices": [{"message": {"content": assistant_content}}]}

    # Подменяем requests.post
    monkeypatch.setattr(ai, "requests", types.SimpleNamespace(post=lambda url, headers, data: FakeResponse()))

    # Запускаем с обычным режимом (без -run)
    monkeypatch.setattr(sys, "argv", ["ai", "тест"])

    ai.main()

    out = capsys.readouterr().out
    # Ожидаем, что форматированный текст был выведен и блок кода обнаружен
    assert "[Блок #1]" in out
    assert "echo hi" in out
    assert "inline" in out or "жирно" in out
    assert "записка" not in out  # проверка: marker "###" не должен быть виден (заменён)


def test_cli_run_mode_executes_selected_block(monkeypatch, capsys):
    ai = _prepare_settings_module()

    monkeypatch.setattr(ai, "get_system_context", lambda: "SYS_CTX")

    assistant_content = "Тестовый ответ\n```sh\n/bin/echo run_ok\n```"

    class FakeResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return {"choices": [{"message": {"content": assistant_content}}]}

    monkeypatch.setattr(ai, "requests", types.SimpleNamespace(post=lambda url, headers, data: FakeResponse()))

    # Подменяем subprocess.run, чтобы не запускать реальные команды
    called = {}
    def fake_run(code, shell=True):
        called['code'] = code
        called['shell'] = shell
        return None
    monkeypatch.setattr(ai.subprocess, "run", fake_run)

    # Эмуляция ввода: сначала выбираем блок 1, затем 0 для выхода
    inputs = iter(["1", "0"])
    monkeypatch.setattr("builtins.input", lambda prompt="": next(inputs))

    monkeypatch.setattr(sys, "argv", ["ai", "-run", "запусти"])

    ai.main()

    out = capsys.readouterr().out
    # Проверяем, что приглашение на выбор блока и вывод блока присутствуют
    assert "Введите номер блока" in out
    assert "Выполняем блок #1" in out or ">>> Выполняем блок #1" in out
    # И что subprocess.run был вызван с ожидаемой командой
    assert 'code' in called
    assert "echo run_ok" in called['code']