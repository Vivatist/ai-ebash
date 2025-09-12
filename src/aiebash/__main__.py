#!/usr/bin/env python3
import sys
from pathlib import Path

# Добавляем parent (src) в sys.path для локального запуска
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

# Сначала импортируем настройки без импорта логгера
from aiebash.settings import settings

# Теперь импортируем и настраиваем логгер
from aiebash.logger import configure_logger

# Получаем настройки логирования и настраиваем логгер
logging_config = settings.get_logging_config()
logger = configure_logger(logging_config)

# Теперь продолжаем импорты остальных модулей
from rich.console import Console
from rich.markdown import Markdown
from aiebash.llm_factory import create_llm_client
from aiebash.arguments import parse_args, parser
from aiebash.chat import chat_loop


# === Считываем глобальные настройки ===
logger.debug("Загрузка настроек...")
CONTEXT: str = settings.get_value("global", "context", "")
BACKEND: str = settings.get_value("global", "backend", "openai_over_proxy")

# Настройки конкретного бэкенда (например, openai_over_proxy)
MODEL = settings.get_value(BACKEND, "model", "")
API_URL = settings.get_value(BACKEND, "api_url", "")
API_KEY = settings.get_value(BACKEND, "api_key", "")

logger.info(f"Используемый бэкенд: {BACKEND}")
logger.info(f"Модель: {MODEL}")
logger.debug(f"API URL: {API_URL}")


# === Инициализация клиента ===
logger.debug("Инициализация LLM клиента...")
try:
    llm_client = create_llm_client(
        backend=BACKEND,
        model=MODEL,
        api_url=API_URL,
        api_key=API_KEY,
    )
    logger.info("Настройки клиента: backend=%s, model=%s", BACKEND, MODEL)
    logger.debug("LLM клиент успешно создан")
except Exception as e:
    logger.error(f"Ошибка при создании LLM клиента: {e}", exc_info=True)
    sys.exit(1)


# === Основная логика ===
def main() -> None:
    logger.info("Запуск ai-ebash")
    logger.debug("Запуск основного процесса...")

    console = Console()

    try:
        args = parse_args()
        logger.debug(f"Полученные аргументы: dialog={args.dialog}, prompt={args.prompt or '(пусто)'}")
        
        chat_mode: bool = args.dialog
        prompt: str = " ".join(args.prompt)

        if chat_mode:
            logger.info("Запуск в режиме диалога")
            try:
                chat_loop(console, llm_client, CONTEXT, prompt or None)
            except Exception as e:
                logger.error(f"Ошибка в режиме диалога: {e}", exc_info=True)
                return 1
        else:
            logger.info("Запуск в режиме одиночного запроса")
            if not prompt:
                logger.warning("Запрос не предоставлен, показываем справку")
                parser.print_help()
                return 1
                
            try:
                logger.debug(f"Отправка запроса: {prompt[:50]}...")
                answer: str = llm_client.send_prompt(prompt, system_context=CONTEXT)
                logger.debug(f"Получен ответ длиной {len(answer)} символов")
            except Exception as e:
                return 1
            
            console.print(Markdown(answer))
            logger.info("Запрос успешно выполнен")

    except KeyboardInterrupt:
        logger.info("Программа прервана пользователем")
        return 130
    except Exception as e:
        logger.critical(f"Необработанная ошибка: {e}", exc_info=True)
        console.print(f"[bold red]Критическая ошибка: {e}[/bold red]")
        return 1
    
    logger.info("Программа завершена успешно")
    return 0


if __name__ == "__main__":
    sys.exit(main())
