# openai_client.py
import json, requests
from typing import List

from .llm_interface import LLMClient
from aiebash.logger import logger
from rich.prompt import Prompt
from rich.console import Console


def _format_api_key_display(api_key: str) -> str:
    """Форматирует отображение API ключа для логирования"""
    if not api_key:
        return "(не задан)"
    elif len(api_key) <= 10:
        return api_key
    else:
        return f"{api_key[:5]}...{api_key[-5:]}"


class OpenAIClientOverProxy(LLMClient):
    def __init__(self, model: str, api_url: str, api_key: str = None, timeout: int = 60):
        super().__init__(timeout=timeout)
        self.model = model
        self.api_url = api_url
        self.api_key = api_key
        logger.info(f"Инициализирован {self.__class__.__name__} с моделью {model}")
        logger.debug(f"API URL: {api_url}, timeout: {timeout}с")

    def configure_llm(self, console: Console) -> dict:
        """
        Настройка параметров OpenAI через прокси.
        Настраивается только модель и API ключ, URL фиксирован.
        """
        console.print("\n[bold]Настройка OpenAI через прокси:[/bold]")

        # Текущие значения
        current_model = getattr(self, 'model', 'gpt-4o-mini')
        current_api_key = getattr(self, 'api_key', '')

        # Настройка модели
        new_model = Prompt.ask("Модель", default=current_model)
        if not new_model.strip():
            new_model = current_model

        # Настройка API ключа
        new_api_key = Prompt.ask("API Key", default=current_api_key)

        # Возвращаем обновленные настройки
        return {
            "model": new_model,
            "api_key": new_api_key,
            "api_url": self.api_url  # URL остается фиксированным
        }

    def _send_chat(self, messages: List[dict]) -> str:
        logger.info(f"Отправка запроса к {self.model} через прокси")

        payload = {"model": self.model, "messages": messages}
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
            logger.debug(f"Используется API-ключ: {_format_api_key_display(self.api_key)}")
        else:
            logger.debug("API-ключ не предоставлен (используется публичный доступ, если поддерживается)")
        try:

            logger.debug(f"Выполняется POST-запрос к {self.api_url}")
            resp = requests.post(self.api_url, headers=headers, json=payload, timeout=self.timeout)

            status_code = resp.status_code
            logger.debug(f"Получен ответ, статус: {status_code}")

            resp.raise_for_status()
            data = resp.json()

            if "usage" in data:
                usage = data["usage"]
                logger.info(f"Использование токенов: prompt={usage.get('prompt_tokens', 0)}, "
                           f"completion={usage.get('completion_tokens', 0)}, "
                           f"total={usage.get('total_tokens', 0)}")

            if "choices" in data and data["choices"]:
                answer = data["choices"][0]["message"]["content"]
                logger.info(f"Получен ответ длиной {len(answer)} символов")
                return answer

            logger.error(f"Неожиданный формат ответа API: {json.dumps(data)[:200]}...")
            raise RuntimeError("Unexpected API response format")

        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP ошибка: {e}", exc_info=True)
            raise
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Ошибка соединения: {e}", exc_info=True)
            raise
        except requests.exceptions.Timeout as e:
            logger.error(f"Таймаут соединения: {e}", exc_info=True)
            raise
        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка запроса: {e}", exc_info=True)
            raise
        except Exception as e:
            logger.error(f"Непредвиденная ошибка: {e}", exc_info=True)
            raise


class OpenAIClient(LLMClient):
    def __init__(self, model: str, api_url: str, api_key: str = None, timeout: int = 60):
        super().__init__(timeout=timeout)
        self.model = model
        self.api_url = api_url
        self.api_key = api_key
        logger.info(f"Инициализирован {self.__class__.__name__} с моделью {model}")
        logger.debug(f"API URL: {api_url}, timeout: {timeout}с")

    def configure_llm(self, console: Console) -> dict:
        """
        Настройка параметров OpenAI (прямое соединение).
        Настраивается только модель и API ключ, URL фиксирован.
        """
        console.print("\n[bold]⚙️  Настройка OpenAI (прямое соединение):[/bold]")

        # Текущие значения
        current_model = getattr(self, 'model', 'gpt-4o-mini')
        current_api_key = getattr(self, 'api_key', '')

        # Настройка модели
        new_model = Prompt.ask("Модель", default=current_model)
        if not new_model.strip():
            new_model = current_model

        # Настройка API ключа
        new_api_key = Prompt.ask("API Key", default=current_api_key)

        # Возвращаем обновленные настройки
        return {
            "model": new_model,
            "api_key": new_api_key,
            "api_url": self.api_url  # URL остается фиксированным
        }

    def _send_chat(self, messages: List[dict]) -> str:
        logger.info(f"Отправка запроса к {self.model} (прямое соединение)")

        payload = {"model": self.model, "messages": messages}
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
            logger.debug(f"Используется API-ключ: {_format_api_key_display(self.api_key)}")
        else:
            logger.warning("API-ключ не предоставлен, запрос может быть отклонен")
        try:
            logger.debug(f"Выполняется POST-запрос к {self.api_url}")
            resp = requests.post(self.api_url, headers=headers, json=payload, timeout=self.timeout)

            status_code = resp.status_code
            logger.debug(f"Получен ответ, статус: {status_code}")

            resp.raise_for_status()
            data = resp.json()

            if "usage" in data:
                usage = data["usage"]
                logger.info(f"Использование токенов: prompt={usage.get('prompt_tokens', 0)}, "
                           f"completion={usage.get('completion_tokens', 0)}, "
                           f"total={usage.get('total_tokens', 0)}")

            if "choices" in data and data["choices"]:
                answer = data["choices"][0]["message"]["content"]
                logger.info(f"Получен ответ длиной {len(answer)} символов")
                return answer

            logger.error(f"Неожиданный формат ответа API: {json.dumps(data)[:200]}...")
            raise RuntimeError("Unexpected API response format")

        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP ошибка: {e}", exc_info=True)
            raise
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Ошибка соединения: {e}", exc_info=True)
            raise
        except requests.exceptions.Timeout as e:
            logger.error(f"Таймаут соединения: {e}", exc_info=True)
            raise
        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка запроса: {e}", exc_info=True)
            raise
        except Exception as e:
            logger.error(f"Непредвиденная ошибка: {e}", exc_info=True)
            raise