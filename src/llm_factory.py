# llm_factory.py
from .llm_interface import LLMClient
from .openai_client import OpenAIClientOverProxy, OpenAIClient
from .default_client import DefaultClient
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
        try:
            return DefaultClient(model=model, api_url=api_url, api_key=api_key, timeout=timeout)
        except :
            raise ValueError(f"Не удается создать LLM клиент для: {backend}")
