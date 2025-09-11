# llm_interface.py
from typing import List
import threading
from rich.console import Console
import threading
import time

from aiebash.error_handling import handle_connection_error



class LLMClient:
    def __init__(self, timeout: int = 60):
        self.timeout = timeout

    def run_progress(self, stop_event: threading.Event) -> None:
        """Визуальный индикатор работы ИИ с точечным спиннером.
        Пока stop_event не установлен, показывает "Аи печатает...".
        """
        console = Console()
        try:
            with console.status("[bold green]Ai печатает...[/bold green]", spinner="dots"):
                while not stop_event.is_set():
                    time.sleep(0.1)
        except KeyboardInterrupt:
            stop_event.set()
            console.print("\n[red]Сатаус бар прервана пользователем (Ctrl+C)[/red]")
            raise


    def send_chat(self, messages: List[dict]) -> str:
        """
        Отправляет сообщения в LLM, отображает прогресс-бар.
        Должен быть переопределён в наследнике.
        """
        stop_event = threading.Event()
        progress_thread = threading.Thread(target=self.run_progress, args=(stop_event,))
        progress_thread.start()
        try:
            result = self._send_chat(messages)
        except KeyboardInterrupt:
            raise
        except Exception as e:
            handle_connection_error(e)
            raise
        finally:
            stop_event.set()
            progress_thread.join()
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
