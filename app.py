from rich.console import Console
from rich.syntax import Syntax

console = Console()

# --- Python ---
python_code = """
def greet(name):
    print(f"Hello, {name}!")

greet("Alice")
"""
syntax_python = Syntax(python_code, "python", theme="monokai", line_numbers=True)
console.print("[bold underline]Python код[/bold underline]")
console.print(syntax_python)

# --- JavaScript ---
js_code = """
function greet(name) {
    console.log(`Hello, ${name}!`);
}
greet("Bob");
"""
syntax_js = Syntax(js_code, "javascript", theme="monokai", line_numbers=True)
console.print("\n[bold underline]JavaScript код[/bold underline]")
console.print(syntax_js)

# --- HTML ---
html_code = """
<!DOCTYPE html>
<html>
<head>
    <title>Test</title>
</head>
<body>
    <h1>Hello World</h1>
</body>
</html>
"""
syntax_html = Syntax(html_code, "html", theme="monokai", line_numbers=True)
console.print("\n[bold underline]HTML код[/bold underline]")
console.print(syntax_html)

# --- SQL ---
sql_code = """
SELECT id, name
FROM users
WHERE age > 18
ORDER BY name;
"""
syntax_sql = Syntax(sql_code, "sql", theme="monokai", line_numbers=True)
console.print("\n[bold underline]SQL код[/bold underline]")
console.print(syntax_sql)

from rich.console import Console
from rich.panel import Panel
from rich.rule import Rule

console = Console()

# ---------------------------
# 1. Panel – простой блок
console.print(Panel("Это обычный блок с текстом"))

# 2. Panel с заголовком и стилем
console.print(Panel("Важное сообщение", title="Заголовок", style="bold cyan"))

# 3. Panel с многострочным текстом
console.print(Panel("""Это многострочный блок.
Можно писать несколько строк,
и Rich корректно их отформатирует.""", title="Многострочный"))

# ---------------------------
# 4. Rule – горизонтальная линия с текстом
console.print(Rule("Разделитель"))

# 5. Rule с выравниванием текста
console.print(Rule("Центрированный текст", align="center"))

# 6. Rule с кастомным стилем
console.print(Rule("Важная секция", style="bold magenta"))

# ---------------------------
# 7. Использование Panels и Rule вместе
console.print(Rule("Начало секции", style="green"))
console.print(Panel("Содержимое секции внутри блока", style="yellow"))
console.print(Rule("Конец секции", style="red"))
