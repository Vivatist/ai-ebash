import argparse


def parse_args() -> argparse.Namespace:
    """
    Разбор аргументов командной строки.
    -c / --chat: включить чатовый режим (многошаговый диалог).
    -r / --run: выполнять bash-блоки из ответа.
    prompt: строка запроса (одиночный режим) или первый вопрос чата.
    """
    parser = argparse.ArgumentParser(
        prog="ai",
        description="CLI для общения с LLM (OpenAI, HuggingFace, Ollama и др.)",
    )
    parser.add_argument(
        "-r",
        "--run",
        action="store_true",
        help="Выполнить найденные bash-блоки",
    )
    parser.add_argument(
        "-c",
        "--chat",
        action="store_true",
        help="Войти в диалоговый режим",
    )
    parser.add_argument(
        "prompt",
        nargs="*",
        help="Ваш запрос к ИИ (если без -c) или первый вопрос чата (если с -c)",
    )
    return parser.parse_args()
