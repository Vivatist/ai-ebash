import subprocess
from rich.console import Console

def run_bash_block(console: Console, code_blocks: list, idx: int) -> None:
    """
    Печатает номер и содержимое блока, выполняет его и выводит результат.
    """
    console.print(f"\n>>> Выполняем блок #{idx}:", style="blue")
    console.print(code_blocks[idx - 1])
    try:
        result = subprocess.run(code_blocks[idx - 1], shell=True, capture_output=True, text=True, encoding='utf-8')
        if result.stdout:
            console.print(f"[green]>>>:[/green]\n{result.stdout}")
        if result.stderr:
            console.print(f"[yellow]>>>Error:[/yellow]\n{result.stderr}")
    except Exception as e:
        console.print(f"[yellow]Ошибка выполнения скрипта: {e}[/yellow]")