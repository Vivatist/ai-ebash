import re
import platform

def annotate_code_blocks(md_text):
    """
    Находит fenced code blocks с языком bash (для Linux) или bat (для Windows),
    собирает их содержимое в список и добавляет над каждым блоком строку-метку.
    Возвращает (annotated_md, list_of_code_strings).
    """
    code_blocks = []
    counter = 0
    
    # Определяем тип системы и соответствующий язык
    # is_windows = platform.system().lower() == "windows"
    # code_lang = "bat" if is_windows else "bash"
    
    # Формируем паттерн в зависимости от ОС
    # pattern = re.compile(r"```" + code_lang + r"[^\n]*\n(.*?)```", re.DOTALL | re.IGNORECASE)

    pattern = re.compile(r"```" + r"[^\n]*\n(.*?)```", re.DOTALL | re.IGNORECASE)


    def repl(m):
        nonlocal counter
        counter += 1
        code = m.group(1).rstrip("\n")
        code_blocks.append(code)
        # label = f"\n**Блок кода {code_lang} [#{counter}]**\n"
        # return label + f"```{code_lang}\n" + code + "\n```"
        label = f"\nБлок кода [#{counter}]\n"
        return label + f"```\n" + code + "\n```"

    annotated = pattern.sub(repl, md_text)
    return annotated, code_blocks