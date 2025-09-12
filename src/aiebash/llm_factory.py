# llm_factory.py
from .llm_interface import LLMClient
from .openai_client import OpenAIClientOverProxy, OpenAIClient
# сюда в будущем можно добавить HuggingFaceClient, OllamaClient и др.

def create_llm_client(backend: str, model: str, api_url: str, api_key: str = None, timeout: int = 60) -> LLMClient:
    backend = backend.lower().strip()
    if backend == "openai_over_proxy":
        return OpenAIClientOverProxy(model=model, api_url=api_url, api_key=api_key, timeout=timeout)
    elif backend == "openai":
        return OpenAIClient(model=model, api_url=api_url, api_key=api_key, timeout=timeout)
    # elif backend == "ollama":
    #     return OllamaClient(...)
    else:
        raise ValueError(f"Неизвестный backend: {backend}")
