import threading
import time
from rich.console import Console


def run_progress(stop_event: threading.Event) -> None:
    """Визуальный индикатор работы ИИ с точечным спиннером.

    Пока stop_event не установлен, показывает "печатает...".
    """
    console = Console()
    with console.status("[bold green]Ai печатает...[/bold green]", spinner="dots"):
        while not stop_event.is_set():
            time.sleep(0.1)
