#!/usr/bin/env python3
import sys
from pathlib import Path

from rich.console import Console
from rich.markdown import Markdown

# Добавляем parent (src) в sys.path для локального запуска
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from aiebash.llm_factory import create_llm_client
from aiebash.formatter_text import annotate_bash_blocks
from aiebash.block_runner import run_code_selection
from aiebash.settings import settings
from aiebash.cli import parse_args
from aiebash.chat import chat_loop


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


# === Основная логика ===
def main() -> None:
    args = parse_args()
    console = Console()

    run_mode: bool = args.run
    chat_mode: bool = args.chat
    prompt: str = " ".join(args.prompt)

    try:
        if chat_mode:
            chat_loop(console, llm_client, CONTEXT, run_mode, prompt or None)
        else:
            if not prompt:
                console.print("[yellow]Ошибка: требуется ввести запрос или использовать -c[/yellow]")
                sys.exit(1)
            try:
                answer: str = llm_client.send_prompt(prompt, system_context=CONTEXT)
            except Exception as e:
                return
            
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
    except KeyboardInterrupt:
        sys.exit(130)




if __name__ == "__main__":
    main()
