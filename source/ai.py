#!/usr/bin/env python3
import sys
import subprocess
from rich.console import Console
from rich.markdown import Markdown
from rich.progress import Progress
import threading
import time
from rich.console import Console
from rich.spinner import Spinner
from time import sleep

from settings import CONTEXT, DEBUG
from formatter_text import annotate_bash_blocks
from api_client import send_prompt  # <- новый интерфейс

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
        answer = send_prompt(prompt, system_context=CONTEXT)

        # Сигнализируем потоку прогресса остановиться
        stop_event.set()
        progress_thread.join()  # Ждём завершения потока

        # В режиме DEBUG выводим исходную (неформатированную) версию ответа
        if DEBUG:
            print("=== RAW RESPONSE (from send_prompt) ===")
            print(answer)
            print("=== /RAW RESPONSE ===\n")

        # Размечаем bash-блоки и получаем список кодов
        annotated_answer, code_blocks = annotate_bash_blocks(answer)
        

        # Если включён режим выполнения и есть блоки кода — предлагаем выбрать
        if run_mode and code_blocks:
            console.print(Markdown(annotated_answer))
            try:
                while True:
                    choice = console.input("[blue]\nВведите номер блока кода для запуска (0 — выход): [/blue]").strip()
                    if choice.lower() in ("0", "q", "exit"):
                        print("Выход.")
                        break
                    if not choice.isdigit():
                        print("Введите число или 0 для выхода.")
                        continue
                    idx = int(choice)
                    if idx < 1 or idx > len(code_blocks):
                        print(f"Неверный номер: у вас {len(code_blocks)} блоков. Попробуйте снова.")
                        continue
                    console.print(f"\n>>> Выполняем блок #{choice}:\n{code_blocks[idx - 1]}\n", style="blue")
                    subprocess.run(code_blocks[idx - 1], shell=True)
            except (EOFError, KeyboardInterrupt):
                print("\nВыход.")
        else:
            console.print(Markdown(annotated_answer))

    except Exception as e:
        # Прочие ошибки (сеть, JSON, и т.д.)
        print("Ошибка:", e)

if __name__ == "__main__":
    main()
