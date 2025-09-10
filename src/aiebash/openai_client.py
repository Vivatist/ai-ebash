# openai_client.py
import json, requests
from typing import List
from .llm_interface import LLMClient

class OpenAIClient(LLMClient):
    def __init__(self, model: str, api_url: str, api_key: str = None, timeout: int = 60):
        self.model = model
        self.api_url = api_url
        self.api_key = api_key
        self.timeout = timeout

    def send_chat(self, messages: List[dict]) -> str:
        payload = {"model": self.model, "messages": messages}
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        resp = requests.post(self.api_url, headers=headers, json=payload, timeout=self.timeout)
        resp.raise_for_status()
        data = resp.json()

        if "choices" in data and data["choices"]:
            return data["choices"][0]["message"]["content"]
        raise RuntimeError("Unexpected API response format")

    def send_prompt(self, prompt: str, system_context: str = "") -> str:
        messages = []
        if system_context:
            messages.append({"role": "system", "content": system_context})
        messages.append({"role": "user", "content": prompt})
        return self.send_chat(messages)
