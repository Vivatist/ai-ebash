#!/usr/bin/env python3
import sys
from pathlib import Path

from rich.console import Console
from rich.markdown import Markdown

# Добавляем parent (src) в sys.path для локального запуска
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from aiebash.llm_factory import create_llm_client
from aiebash.formatter_text import annotate_code_blocks
from aiebash.block_runner import run_code_selection
from aiebash.settings import settings
from aiebash.arguments import parse_args
from aiebash.chat import chat_loop


# === Считываем глобальные настройки ===
DEBUG_MODE: bool   = settings.get_value("global", "debug", False)
CONTEXT: str  = settings.get_value("global", "context", "")
BACKEND: str  = settings.get_value("global", "backend", "openai_over_proxy")

# Настройки конкретного бэкенда (например, openai_over_proxy)
MODEL = settings.get_value(BACKEND, "model", "")
API_URL = settings.get_value(BACKEND, "api_url", "")
API_KEY = settings.get_value(BACKEND, "api_key", "")


# === Инициализация клиента ===
llm_client = create_llm_client(
    backend=BACKEND,
    model=MODEL,
    api_url=API_URL,
    api_key=API_KEY,
)


# === Основная логика ===
def main() -> None:
    console = Console()

    args = parse_args()
    chat_mode: bool = args.dialog
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
            
            if DEBUG_MODE:
                print("=== RAW RESPONSE ===")
                print(answer)
                print("=== /RAW RESPONSE ===")
            
            annotated_answer, code_blocks = annotate_code_blocks(answer)

            if run_mode and code_blocks:
                console.print(Markdown(annotated_answer))
                run_code_selection(console, code_blocks)
            else:
                console.print(Markdown(answer))
    except KeyboardInterrupt:
        sys.exit(130)




if __name__ == "__main__":
    main()
