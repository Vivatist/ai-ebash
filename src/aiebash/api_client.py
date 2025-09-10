#!/usr/bin/env python3
"""
api_client — небольшой интерфейс для отправки chat-запросов к API.
Экспортирует send_chat_request (работает с messages) и удобный send_prompt.
"""
import json
import requests
import typing as t


def send_chat_request(messages: t.List[dict], model , api_url, api_key = None, timeout: int = 60) -> dict:
    """
    Отправляет chat-style запрос (messages) к API и возвращает распарсенный JSON-ответ.
    messages — список словарей вида {"role": "user|system|assistant", "content": "..."}.
    """
    if not api_url:
        raise RuntimeError("API_URL не задан в config.ini")

    payload = {
        "model": model,
        "messages": messages,
    }

    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    resp = requests.post(api_url, headers=headers, data=json.dumps(payload), timeout=timeout)
    resp.raise_for_status()
    data = resp.json()

    return data


def send_prompt(prompt: str, model, api_url,api_key = None, system_context: str = "", timeout: int = 30) -> str:
    """
    Удобная обёртка: формирует messages из system_context + user prompt,
    отправляет запрос и возвращает текст ответа ассистента.
    """
    messages = []
    if system_context:
        messages.append({"role": "system", "content": system_context})
    messages.append({"role": "user", "content": prompt})

    data = send_chat_request(messages, model, api_url=api_url, api_key=api_key, timeout=timeout)
    # ожидаемый формат: choices -> [ { message: { content: "..." } } ]
    if "choices" in data and data["choices"]:
        return data["choices"][0]["message"]["content"]
    raise RuntimeError("Unexpected API response format")