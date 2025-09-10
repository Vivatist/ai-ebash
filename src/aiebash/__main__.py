#!/usr/bin/env python3
import sys
import time
import threading
import argparse
from pathlib import Path
from typing import List, Dict

from rich.console import Console
from rich.markdown import Markdown
from rich.rule import Rule

# Добавляем parent (src) в sys.path для локального запуска
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from aiebash.llm_factory import create_llm_client
from aiebash.formatter_text import annotate_bash_blocks
from aiebash.block_runner import run_code_selection
from aiebash.settings import settings


# === Считываем глобальные настройки ===
DEBUG: bool   = settings.get_bool("global", "DEBUG")
CONTEXT: str  = settings.get("global", "CONTEXT")
BACKEND: str  = settings.get("global", "BACKEND")

# Настройки конкретного бэкенда (например, openai_over_proxy)
MODEL: str    = settings.get(BACKEND, "MODEL")
API_URL: str  = settings.get(BACKEND, "API_URL")
API_KEY: str  = settings.get(BACKEND, "API_KEY")


# === Инициализация клиента ===
llm_client = create_llm_client(
    backend=BACKEND,
    model=MODEL,
    api_url=API_URL,
    api_key=API_KEY,
)


# === Прогресс-бар ===
stop_event = threading.Event()

def run_progress() -> None:
    """
    Визуальный индикатор работы ИИ.
    Пока stop_event не установлен, показывает "печатает..." со спиннером.
    """
    console = Console()
    with console.status("[bold green]Ai печатает...[/bold green]", spinner="dots"):
        while not stop_event.is_set():
            time.sleep(0.1)


# === Аргументы ===
def parse_args() -> argparse.Namespace:
    """
    Разбор аргументов командной строки.
    -c / --chat: включить чатовый режим (многошаговый диалог).
    -r / --run: выполнять bash-блоки из ответа.
    prompt: строка запроса (одиночный режим) или первый вопрос чата.
    """
    parser = argparse.ArgumentParser(
        prog="ai",
        description="CLI для общения с LLM (OpenAI, HuggingFace, Ollama и др.)"
    )
    parser.add_argument(
        "-r", "--run",
        action="store_true",
        help="Выполнить найденные bash-блоки"
    )
    parser.add_argument(
        "-c", "--chat",
        action="store_true",
        help="Войти в диалоговый режим"
    )
    parser.add_argument(
        "prompt",
        nargs="*",
        help="Ваш запрос к ИИ (если без -c) или первый вопрос чата (если с -c)"
    )
    return parser.parse_args()


# === Основная логика ===
def main() -> None:
    args = parse_args()
    console = Console()

    run_mode: bool = args.run
    chat_mode: bool = args.chat
    prompt: str = " ".join(args.prompt)

    try:
        # --- Чатовый режим ---
        if chat_mode:
            console.print(Rule(" Вход в чатовый режим ", style="cyan"))
            messages: List[Dict[str, str]] = []
            if CONTEXT:
                messages.append({"role": "system", "content": CONTEXT})

            def handle_answer(answer: str) -> List[str]:
                """
                Обработка ответа ассистента:
                - вывод метки AI,
                - подсветка и вывод markdown,
                - возвращает список bash-блоков (если есть).
                """
                console.print("[bold blue]AI:[/bold blue]")
                annotated_answer, code_blocks = annotate_bash_blocks(answer)
                console.print(Markdown(annotated_answer))
                console.print(Rule("", style="green"))
                return code_blocks

            # Первый вопрос можно задать сразу после -c
            if prompt:
                messages.append({"role": "user", "content": prompt})

                stop_event.clear()
                progress_thread = threading.Thread(target=run_progress)
                progress_thread.start()

                answer: str = llm_client.send_chat(messages)

                stop_event.set()
                progress_thread.join()

                messages.append({"role": "assistant", "content": answer})
                last_code_blocks = handle_answer(answer)
            else:
                last_code_blocks = []

            # Основной цикл диалога
            while True:
                try:
                    user_input: str = console.input("[bold green]Вы:[/bold green] ")

                    if user_input.strip().lower() in ("exit", "quit", "выход"):
                        break

                    # === Запуск блоков ===
                    if last_code_blocks:
                        # Если -r и ввод — число → запуск блока
                        if run_mode and user_input.strip().isdigit():
                            idx = int(user_input.strip()) - 1
                            if 0 <= idx < len(last_code_blocks):
                                run_code_selection(console, [last_code_blocks[idx]])
                            continue

                        # Если ввод начинается с :run → запуск блока
                        if user_input.strip().startswith(":run"):
                            parts = user_input.strip().split()
                            if len(parts) == 1:
                                idx = 0
                            else:
                                try:
                                    idx = int(parts[1]) - 1
                                except ValueError:
                                    console.print("[red]Неверный формат команды :run[/red]")
                                    continue

                            if 0 <= idx < len(last_code_blocks):
                                run_code_selection(console, [last_code_blocks[idx]])
                            else:
                                console.print("[red]Нет такого блока[/red]")
                            continue

                    # === Обычный вопрос ===
                    messages.append({"role": "user", "content": user_input})

                    stop_event.clear()
                    progress_thread = threading.Thread(target=run_progress)
                    progress_thread.start()

                    answer: str = llm_client.send_chat(messages)

                    stop_event.set()
                    progress_thread.join()

                    messages.append({"role": "assistant", "content": answer})
                    last_code_blocks = handle_answer(answer)

                except KeyboardInterrupt:
                    console.print("\n[red]Выход из чата по Ctrl+C[/red]")
                    break

        # --- Обычный режим ---
        else:
            if not prompt:
                console.print("[red]Ошибка: требуется ввести запрос или использовать -c[/red]")
                sys.exit(1)

            # Показываем прогрессбар
            stop_event.clear()
            progress_thread = threading.Thread(target=run_progress)
            progress_thread.start()

            answer: str = llm_client.send_prompt(prompt, system_context=CONTEXT)

            stop_event.set()
            progress_thread.join()

            if DEBUG:
                print("=== RAW RESPONSE ===")
                print(answer)
                print("=== /RAW RESPONSE ===")

            annotated_answer, code_blocks = annotate_bash_blocks(answer)

            if run_mode and code_blocks:
                console.print(Markdown(annotated_answer))
                run_code_selection(console, code_blocks)
            else:
                console.print(Markdown(answer))

            console.print(Rule("", style="green"))

    except Exception as e:
        print("Ошибка:", e)


if __name__ == "__main__":
    main()
