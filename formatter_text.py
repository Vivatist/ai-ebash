import re

# ANSI цвета и стили
YELLOW = "\033[33m"
GRAY_ITALIC = "\033[90m\033[3m"
GREEN = "\033[32m"
BOLD = "\033[1m"
RESET = "\033[0m"

def highlight_code_blocks(text):
    """Подсветка блоков кода в жёлтый и нумерация"""
    code_blocks = []
    def repl(match):
        code = match.group(1)
        code_blocks.append(code.strip())
        index = len(code_blocks)
        return f"{YELLOW}[Блок #{index}]\n{code}{RESET}"
    pattern = re.compile(r"```.*?\n(.*?)```", re.DOTALL)
    formatted = pattern.sub(repl, text)
    return formatted, code_blocks

def highlight_explanation_blocks(text):
    """Подсветка блоков между ### ... ### в серый курсив"""
    def repl(match):
        content = match.group(1).strip()
        return f"{GRAY_ITALIC}{content}{RESET}"
    pattern = re.compile(r"###(.*?)###", re.DOTALL)
    return pattern.sub(repl, text)

def highlight_inline_code(text):
    """Подсветка инлайн-кода `...` в зелёный"""
    def repl(match):
        code = match.group(1)
        return f"{GREEN}{code}{RESET}"
    pattern = re.compile(r"`([^`]+)`")
    return pattern.sub(repl, text)

def highlight_bold(text):
    """Подсветка текста между **...** жирным"""
    def repl(match):
        bold_text = match.group(1)
        return f"{BOLD}{bold_text}{RESET}"
    pattern = re.compile(r"\*\*(.*?)\*\*")
    return pattern.sub(repl, text)

def format_answer(text):
    """Применяем все правила форматирования и возвращаем текст + блоки кода"""
    text, code_blocks = highlight_code_blocks(text)
    text = highlight_explanation_blocks(text)
    text = highlight_inline_code(text)
    text = highlight_bold(text)
    return text, code_blocks
