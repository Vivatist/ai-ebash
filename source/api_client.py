#!/usr/bin/env python3
"""
api_client — небольшой интерфейс для отправки chat-запросов к API.
Экспортирует send_chat_request (работает с messages) и удобный send_prompt.
"""
import json
import requests
import typing as t
import settings

API_URL = getattr(settings, "API_URL", "")
DEFAULT_MODEL = getattr(settings, "MODEL", None)
API_KEY = getattr(settings, "API_KEY", None)
DEBUG = getattr(settings, "DEBUG", False)


def send_chat_request(messages: t.List[dict], model: t.Optional[str] = None, timeout: int = 60) -> dict:
    """
    Отправляет chat-style запрос (messages) к API и возвращает распарсенный JSON-ответ.
    messages — список словарей вида {"role": "user|system|assistant", "content": "..."}.
    """
    if not API_URL:
        raise RuntimeError("API_URL не задан в settings.py")

    payload = {
        "model": model or DEFAULT_MODEL,
        "messages": messages,
    }

    headers = {"Content-Type": "application/json"}
    if API_KEY:
        headers["Authorization"] = f"Bearer {API_KEY}"

    resp = requests.post(API_URL, headers=headers, data=json.dumps(payload), timeout=timeout)
    resp.raise_for_status()
    data = resp.json()

    if DEBUG:
        print("=== RAW API RESPONSE ===")
        print(json.dumps(data, ensure_ascii=False, indent=2))
        print("=== /RAW API RESPONSE ===\n")

    return data


def send_prompt(prompt: str, system_context: str = "", model: t.Optional[str] = None, timeout: int = 60) -> str:
    """
    Удобная обёртка: формирует messages из system_context + user prompt,
    отправляет запрос и возвращает текст ответа ассистента.
    """
    messages = []
    if system_context:
        messages.append({"role": "system", "content": system_context})
    messages.append({"role": "user", "content": prompt})

    data = send_chat_request(messages, model=model, timeout=timeout)
    # ожидаемый формат: choices -> [ { message: { content: "..." } } ]
    if "choices" in data and data["choices"]:
        return data["choices"][0]["message"]["content"]
    raise RuntimeError("Unexpected API response format")