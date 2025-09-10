#!/usr/bin/env python3
import subprocess
from rich.console import Console
from rich.markdown import Markdown


def run_code_selection(console: Console, code_blocks: list):
    """
    Интерактивный цикл: спрашивает номер блока, выводит его содержимое и при выборе выполняет его.
    Завершается при вводе 0, q, exit или при Ctrl+C / EOF.
    """
    try:
        while True:
            choice = console.input("[blue]\nВведите номер блока кода для запуска (0 — выход): [/blue]").strip()
            if choice.lower() in ("0", "q", "exit"):
                console.print("Выход.")
                break
            if not choice.isdigit():
                console.print("[red]Введите число или 0 для выхода.[/red]")
                continue
            idx = int(choice)
            if idx < 1 or idx > len(code_blocks):
                console.print(f"[red]Неверный номер: у вас {len(code_blocks)} блоков. Попробуйте снова.[/red]")
                continue
            console.print(f"\n>>> Выполняем блок #{idx}:\n", style="blue")
            console.print(code_blocks[idx - 1])
            # Выполнение — риск: выполняется произвольный код из ответа ИИ
            subprocess.run(code_blocks[idx - 1], shell=True)
    except (EOFError, KeyboardInterrupt):
        console.print("\nВыход.")