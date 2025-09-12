
# --- Top-level imports ---
from typing import List, Dict, Optional
from rich.console import Console
from rich.markdown import Markdown
from aiebash.formatter_text import annotate_code_blocks
from aiebash.script_executor import run_code_block
from aiebash.settings import settings


def _render_answer(console: Console, answer: str) -> List[str]:
    """Отрисовать ответ AI. При run_mode=True нумеруем bash-блоки, иначе просто показываем текст.
    Возвращает список bash-блоков (только при run_mode=True), иначе пустой список.
    """
    console.print("[bold blue]AI:[/bold blue]")
    annotated_answer, code_blocks = annotate_code_blocks(answer)
    
    DEBUG_MODE: bool = bool(str(settings.get_value("global", "debug", False)).lower() == "true")
    print(f"DEBUG_MODE: {DEBUG_MODE}")
    
    if DEBUG_MODE:
                print("=== RAW RESPONSE ===")
                print(answer)
                print("=== /RAW RESPONSE ===")
    console.print(Markdown(annotated_answer))
    return code_blocks

def chat_loop(console: Console, llm_client, context: str, first_prompt: Optional[str]) -> None:
    messages: List[Dict[str, str]] = []
    if context:
        messages.append({"role": "system", "content": context})

    code_blocks: List[str] = []

    # Первый вопрос
    if first_prompt:
        messages.append({"role": "user", "content": first_prompt})
        answer: str = llm_client.send_chat(messages)
        messages.append({"role": "assistant", "content": answer})
        code_blocks = _render_answer(console, answer)

    # Основной цикл
    while True:
        try:
            # Ввод пользователя
            # Вывод подсказки в зависимости от наличия блоков кода
            if len(code_blocks) > 0:
                console.print("[dim]Введите следующий вопрос или номер блока кода для немедленного выполнения[/dim]")
            else:
                console.print("[dim]Введите следующий вопрос[/dim]")
            user_input: str = console.input("[bold green]Вы:[/bold green] ")
            stripped = user_input.strip()
            if stripped.lower() in ("exit", "quit", "выход"):
                break

            # Если режим запуска включен и введено число — попытка запуска блока
            if stripped.isdigit():
                idx = int(stripped)
                if 1 <= idx <= len(code_blocks):
                    run_code_block(console, code_blocks, idx)
                else:
                    console.print("[yellow]Нет такого блока. Введите номер из списка или текстовый запрос.[/yellow]")
                continue  # Возвращаемся к вводу промпта

            # Обычное сообщение пользователя
            messages.append({"role": "user", "content": user_input})
            try:
                answer = llm_client.send_chat(messages)
            except Exception as e:
                pass
            messages.append({"role": "assistant", "content": answer})
            code_blocks = _render_answer(console, answer)

        except KeyboardInterrupt:
            console.print("\n")
            break
