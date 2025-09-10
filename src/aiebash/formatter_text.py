import re

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