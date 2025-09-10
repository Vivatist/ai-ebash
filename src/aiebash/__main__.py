#!/usr/bin/env python3
import sys
from pathlib import Path

# Убедимся, что parent (src) в sys.path, чтобы можно было import aibash.*
# Это нужно, если вы запускаете файл напрямую: python src/aibash/__main__.py
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


from rich.markdown import Markdown
from rich.console import Console
from rich.rule import Rule
import threading
import time


from aiebash.api_client import send_prompt
from aiebash.formatter_text import annotate_bash_blocks
from aiebash.block_runner import run_code_selection  # добавлен импорт

from aiebash.settings import settings as user_settings

# нормализуем DEBUG (возможные варианты: True/False, "true"/"False", "1"/"0")
_raw_debug = user_settings.get("DEBUG")
if isinstance(_raw_debug, bool):
    DEBUG = _raw_debug
else:
    DEBUG = str(_raw_debug).strip().lower() in ("1", "true", "yes", "on")
CONTEXT = user_settings.get("CONTEXT")
MODEL = user_settings.get("MODEL")
API_URL = user_settings.get("API_URL")
API_KEY = user_settings.get("API_KEY")

# Флаг для остановки потока (заменён на Event)
import threading
stop_event = threading.Event()

def run_progress():
    console = Console()
    with console.status("[bold green]Ai печатает...[/bold green]", spinner="dots") as status:
         while not stop_event.is_set():
            time.sleep(0.1)

def main():
    # Если нет аргументов, выводим подсказку по использованию
    if len(sys.argv) < 2:
        print("Использование: ai [-run] ваш запрос к ИИ без кавычек")
        sys.exit(0)

    console = Console()

    # Проверяем ключ -run
    run_mode = False
    args = sys.argv[1:]
    if "-run" in args:
        run_mode = True
        args.remove("-run")

    # Собираем текст запроса из оставшихся аргументов
    prompt = " ".join(args)

    try:
        # Запуск прогресс-бара в отдельном потоке
        progress_thread = threading.Thread(target=run_progress)
        progress_thread.start()

        # Получаем ответ от API через новый интерфейс
        answer = send_prompt(prompt, MODEL, API_URL, API_KEY, CONTEXT)

        # Сигнализируем потоку прогресса остановиться
        stop_event.set()
        progress_thread.join()  # Ждём завершения потока

        # В режиме DEBUG выводим исходную (неформатированную) версию ответа
        if not DEBUG:
            print("=== RAW RESPONSE (from send_prompt) ===")
            print(answer)
            print("=== /RAW RESPONSE === \n")

        # Размечаем bash-блоки и получаем список кодов
        annotated_answer, code_blocks = annotate_bash_blocks(answer)
        

        # Если включён режим выполнения и есть блоки кода — предлагаем выбрать
        if run_mode and code_blocks:
            console.print(Markdown(annotated_answer))
            run_code_selection(console, code_blocks)
        else:
            console.print(Markdown(answer))
        
        console.print(Rule("", style="green"))

    except Exception as e:
        # Прочие ошибки (сеть, JSON, и т.д.)
        print("Ошибка:", e)



if __name__ == "__main__":
    main()
