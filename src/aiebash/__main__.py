#!/usr/bin/env python3
import sys
from pathlib import Path

# Добавляем parent (src) в sys.path для локального запуска
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

# Сначала импортируем настройки без импорта логгера
from aiebash.config_manager import config_manager

# Теперь импортируем и настраиваем логгер
from aiebash.logger import configure_logger

# Получаем настройки логирования и настраиваем логгер
logging_config = config_manager.get_logging_config()
logger = configure_logger(logging_config)

# Теперь продолжаем импорты остальных модулей
from rich.console import Console
from rich.markdown import Markdown
from aiebash.llm_factory import create_llm_client
from aiebash.arguments import parse_args, parser
from aiebash.chat import chat_loop


# === Считываем глобальные настройки ===
logger.info("Загрузка настроек...")
CONTEXT: str = config_manager.get_value("global", "context", "")
CURRENT_LLM: str = config_manager.get_value("global", "current_LLM", "openai_over_proxy")

logger.debug(f"Заданы настройки - Системный контекст: {'(пусто)' if not CONTEXT else CONTEXT[:30] + '...'}")
logger.debug(f"Заданы настройки - Текущий LLM: {CURRENT_LLM}")

# Настройки конкретного LLM (например, openai_over_proxy)
MODEL = config_manager.get_value("supported_LLMs", CURRENT_LLM, {}).get("model", "")
API_URL = config_manager.get_value("supported_LLMs", CURRENT_LLM, {}).get("api_url", "")
API_KEY = config_manager.get_value("supported_LLMs", CURRENT_LLM, {}).get("api_key", "")

logger.debug(f"Заданы настройки - Модель: {MODEL}")
logger.debug(f"Заданы настройки - API URL: {API_URL}")
logger.debug(f"Заданы настройки - API Key: {'(не задан)' if not API_KEY else f'{API_KEY[:5]}...{API_KEY[-5:] if len(API_KEY) > 10 else API_KEY}'}")


# === Инициализация клиента ===
logger.debug("Инициализация LLM клиента %s", CURRENT_LLM)
try:
    llm_client = create_llm_client(
        backend=CURRENT_LLM,
        model=MODEL,
        api_url=API_URL,
        api_key=API_KEY,
    )
except Exception as e:
    logger.error(f"Ошибка при создании LLM клиента: {e}", exc_info=True)
    sys.exit(1)


# === Основная логика ===
def main() -> None:

    console = Console()

    try:
        args = parse_args()
        logger.info("Разбор аргументов командной строки...")
        logger.debug(f"Полученные аргументы: dialog={args.dialog}, settings={args.settings}, prompt={args.prompt or '(пусто)'}")
        
        # Обработка режима настройки
        if args.settings:
            logger.info("Запуск конфигурационного режима")
            try:
                from aiebash.config_manager import run_configuration_dialog
                run_configuration_dialog()
                logger.info("Конфигурационный режим завершен")
                return 0
            except Exception as e:
                logger.error(f"Ошибка в режиме конфигурации: {e}", exc_info=True)
                return 1
        
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
                logger.debug(f"Отправка запроса: '{prompt[:50]}'...")
                answer: str = llm_client.send_prompt(prompt, system_context=CONTEXT)
            except Exception as e:
                return 1
            
            console.print(Markdown(answer))
            logger.info("Запрос успешно выполнен")

    except KeyboardInterrupt:
        logger.info("Программа прервана пользователем")
        return 130
    except Exception as e:
        logger.critical(f"Необработанная ошибка: {e}", exc_info=True)
        return 1
    
    logger.info("Программа завершена успешно")
    return 0


if __name__ == "__main__":
    sys.exit(main())
