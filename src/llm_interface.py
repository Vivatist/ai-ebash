# llm_interface.py
from typing import List
import threading
from rich.console import Console
import threading
import time

from aiebash.error_handling import handle_connection_error
from aiebash.logger import log_execution_time


class LLMClient:
    def __init__(self, timeout: int = 60):
        self.timeout = timeout

    def run_progress(self, stop_spinner: threading.Event) -> None:
        """Визуальный индикатор работы ИИ с точечным спиннером.
        Пока stop_event не установлен, показывает "Аи печатает...".
        """
        console = Console()
        with console.status("[dim]Ai печатает...[/dim]", spinner="dots", spinner_style="dim"):
            while not stop_spinner.is_set():
                time.sleep(0.1)

        

    @log_execution_time # декоратор логирования времени исполнениения
    def send_chat(self, messages: List[dict]) -> str:
        """
        Отправляет сообщения в LLM, отображает прогресс-бар.
        Должен быть переопределён в наследнике.
        """
        stop_spinner = threading.Event()
        progress_thread = threading.Thread(target=self.run_progress, args=(stop_spinner,), daemon=True)
        progress_thread.start()
        
        result = None
        error = None
        
        try:
            result = self._send_chat(messages)
        except KeyboardInterrupt:
            raise
        except Exception as e:
            # Сохраняем ошибку, но НЕ обрабатываем её здесь
            error = e
        finally:
            # 1. Останавливаем поток индикатора
            stop_spinner.set()
            # 2. Ждем завершения потока индикатора
            progress_thread.join(timeout=1.0)
            # 3. Небольшая пауза для гарантированного обновления консоли
            time.sleep(0.1)
        
        # 4. Только ПОСЛЕ полной очистки индикатора обрабатываем ошибку
        if error:
            handle_connection_error(error)
            raise error
            
        return result


    def _send_chat(self, messages: List[dict]) -> str:
        """
        Реализация отправки запроса к LLM. Переопределяется в наследнике.
        """
        raise NotImplementedError

    def send_prompt(self, prompt: str, system_context: str = "") -> str:
        messages = []
        if system_context:
            messages.append({"role": "system", "content": system_context})
        messages.append({"role": "user", "content": prompt})
        return self.send_chat(messages)

    def configure_llm(self, console: Console) -> dict:
        """
        Интерактивная настройка параметров LLM.
        Возвращает словарь с обновленными настройками.
        Должен быть переопределён в наследнике.
        """
        raise NotImplementedError("Метод configure_llm должен быть реализован в наследнике")
