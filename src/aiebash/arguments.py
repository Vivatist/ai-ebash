import argparse


def parse_args() -> argparse.Namespace:
    """
    Разбор аргументов командной строки.
    -d / --dialog: включить диалоговый режим с возможностью выполнения блоков кода из ответа ИИ.
    """
    parser = argparse.ArgumentParser(
        prog="ai",
        description=(
            "Утилита для для общения с нейросетью "
            "(OpenAI, HuggingFace, Ollama и др.) "
            "не покидая командной строки."
        ),
        epilog="Пример: ai -d Напиши bash-скрипт для резервного копирования файлов."
    )

    parser.add_argument(
        "-d",
        "--dialog",
        action="store_true",
        help=(
            "Режим диалога с возможностью выполнять блоки кода из ответа. "
            "Выход из диалога: exit, quit, выход или Ctrl+C."
        )
    )

    parser.add_argument(
        "prompt",
        nargs="*",
        help="Ваш запрос к ИИ.",
    )
    return parser.parse_args()
