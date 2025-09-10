# llm_factory.py
from .llm_interface import LLMClient
from .openai_client import OpenAIClient
# сюда в будущем можно добавить HuggingFaceClient, OllamaClient и др.

def create_llm_client(backend: str, model: str, api_url: str, api_key: str = None, timeout: int = 60) -> LLMClient:
    backend = backend.lower().strip()
    if backend == "openai_over_proxy":
        return OpenAIClient(model=model, api_url=api_url, api_key=api_key, timeout=timeout)
    # elif backend == "huggingface":
    #     return HuggingFaceClient(...)
    # elif backend == "ollama":
    #     return OllamaClient(...)
    else:
        raise ValueError(f"Неизвестный backend: {backend}")
