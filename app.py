#!/usr/bin/env python3
import sys
import re
from pathlib import Path
from rich.console import Console
from rich.markdown import Markdown

def annotate_bash_blocks(md_text):
    """
    Находит fenced code blocks с языком bash, собирает их содержимое в список
    и добавляет над каждым блоком строку-метку вида "**Блок кода bash [#{counter}]**".
    Возвращает (annotated_md, list_of_code_strings).
    """
    code_blocks = []
    counter = 0

    pattern = re.compile(r"```bash[^\n]*\n(.*?)```", re.DOTALL | re.IGNORECASE)

    def repl(m):
        nonlocal counter
        counter += 1
        code = m.group(1).rstrip("\n")
        code_blocks.append(code)
        label = f"\n**Блок кода bash [#{counter}]**\n"
        return label + "```bash\n" + code + "\n```"

    annotated = pattern.sub(repl, md_text)
    return annotated, code_blocks

def main():
    console = Console()
    # Путь к файлу можно передать как аргумент, по умолчанию ./text.md
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("text.md")
    if not path.exists():
        console.print(f"[red]Файл не найден:[/red] {path}")
        sys.exit(1)

    md_text = path.read_text(encoding="utf-8")
    annotated_md, blocks = annotate_bash_blocks(md_text)

    # Рендерим форматированный Markdown через rich
    console.print(Markdown(annotated_md))

    # Интерактивный цикл: ожидание номера блока и вывод его сырого содержимого
    if not blocks:
        print("\n(Блоки bash не найдены)")
        return

    try:
        while True:
            choice = input("\nВведите номер блока для просмотра (0 — выход): ").strip()
            if choice.lower() in ("0", "q", "exit"):
                print("Выход.")
                break
            if not choice.isdigit():
                print("Введите число или 0 для выхода.")
                continue
            idx = int(choice)
            if idx < 1 or idx > len(blocks):
                print(f"Неверный номер: у вас {len(blocks)} блоков. Попробуйте снова.")
                continue
            print(f"\n--- Блок #{idx} (сырое содержимое) ---")
            print(blocks[idx - 1])
    except (EOFError, KeyboardInterrupt):
        print("\nВыход.")

if __name__ == "__main__":
    main()