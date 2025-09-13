import argparse

# Создаем парсер как объект модуля
parser = argparse.ArgumentParser(
    prog="ai",
    description=(
        "Утилита для общения с нейросетью "
        "(OpenAI, HuggingFace, Ollama и др.) "
        "не покидая командной строки."
    ),
)

parser.add_argument(
    "-d",
    "--dialog",
    action="store_true",
    help=(
        "Режим диалога с возможностью выполнять блоки кода из ответа. "
        "Выход из диалога: exit, quit, выход или Ctrl+C."
    ),
)

parser.add_argument(
    "-s",
    "--settings",
    action="store_true",
    help="Запуск интерактивного режима настройки приложения.",
)

parser.add_argument(
    "prompt",
    nargs="*",
    help="Ваш запрос к ИИ.",
)


def parse_args() -> argparse.Namespace:
    """
    Разбор аргументов командной строки.
    """
    return parser.parse_args()
