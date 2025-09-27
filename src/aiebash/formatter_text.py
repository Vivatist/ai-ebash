import re
from aiebash.i18n import t


def format_api_key_display(api_key: str) -> str:
    """Форматирует отображение API ключа для логирования
    показывает первые и последние 5 символов, остальное заменяет на "...".
    """
    if not api_key:
        return t("(not set)")
    elif len(api_key) <= 10:
        return api_key
    else:
        return f"{api_key[:5]}...{api_key[-5:]}"


def extract_labeled_code_blocks(text: str) -> list[str]:
    """
    Извлекает содержимое блоков кода, у которых сверху есть подпись в квадратных скобках.
    Подпись может быть любой: [Код #1], [Пример], [Test], и т.п.
    """
    pattern = r"\[[^\]]+\]\s*```.*?\n(.*?)```"
    matches = re.findall(pattern, text, flags=re.DOTALL)
    return [m.strip() for m in matches]
