# openai_client.py
import json, requests
import sys
from typing import List

from aiebash.error_handling import handle_connection_error
from .llm_interface import LLMClient

class OpenAIClient(LLMClient):
    def __init__(self, model: str, api_url: str, api_key: str = None, timeout: int = 60):
        super().__init__(timeout=timeout)
        self.model = model
        self.api_url = api_url
        self.api_key = api_key

    def _send_chat(self, messages: List[dict]) -> str:
        payload = {"model": self.model, "messages": messages}
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        try:
            resp = requests.post(self.api_url, headers=headers, json=payload, timeout=self.timeout)
        except: 
            raise
        resp.raise_for_status()
        data = resp.json()
        if "choices" in data and data["choices"]:
            return data["choices"][0]["message"]["content"]
        raise RuntimeError("Unexpected API response format")
