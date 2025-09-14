import logging
import json
import sys
from pathlib import Path
from typing import Dict, Any, Optional
from rich.logging import RichHandler
from rich.console import Console
from rich.traceback import install
import platform
from logging.handlers import RotatingFileHandler
from platformdirs import user_config_dir

# Константы
APP_NAME = "ai-ebash"
log_dir = Path(user_config_dir(APP_NAME)) / "logs"
log_dir.mkdir(parents=True, exist_ok=True)

# Заглушка для логгера по умолчанию (будет заменен)
logger = logging.getLogger('ai-ebash')

# Устанавливаем Rich для форматирования трейсбеков
install(show_locals=True)

# Преобразование строковых уровней в константы logging
def get_log_level(level_name: str) -> int:
    """Преобразует строковое имя уровня логирования в константу logging"""
    level_map = {
        "debug": logging.DEBUG,
        "info": logging.INFO,
        "warning": logging.WARNING,
        "error": logging.ERROR,
        "critical": logging.CRITICAL
    }
    return level_map.get(level_name.lower(), logging.INFO)

def configure_logger(config_data: Optional[Dict] = None) -> logging.Logger:
    """
    Настраивает и возвращает логгер с указанными параметрами.
    
    Args:
        config_data: Настройки логирования из конфигурации
    
    Returns:
        logging.Logger: Настроенный логгер
    """
    global logger
    
    # Значения по умолчанию
    log_level = logging.INFO
    console_level = logging.CRITICAL
    file_level = logging.DEBUG
    file_enabled = True
    
    # Применяем настройки из конфигурации, если они есть
    if config_data:      
        log_level = get_log_level(config_data.get('level', 'DEBUG'))
        console_level = get_log_level(config_data.get('console_level', 'DEBUG'))
        file_level = get_log_level(config_data.get('file_level', 'DEBUG'))
        file_enabled = config_data.get('file_enabled', True)
    
    # Создаем новый логгер
    logger = logging.getLogger('ai-ebash')
    logger.setLevel(log_level)
    
    # Очистка существующих обработчиков
    if logger.hasHandlers():
        logger.handlers.clear()
    
    # Консольный вывод
    console = Console()
    console_handler = RichHandler(
        console=console,
        rich_tracebacks=True,
        markup=True,
        show_path=False
    )
    console_handler.setLevel(console_level)
    logger.addHandler(console_handler)
    
    # Файловый вывод
    if file_enabled:
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
        )
        file_handler = RotatingFileHandler(
            log_dir / "ai-ebash.log", 
            maxBytes=5*1024*1024,
            backupCount=3,
            encoding='utf-8'
        )
        file_handler.setLevel(file_level)
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    
    # Логируем системную информацию при запуске
    logger.info(f"Запуск ai-ebash на {platform.system()} {platform.release()}")
    logger.debug(f"Python {platform.python_version()}, интерпретатор: {sys.executable}")
    logger.debug(f"Уровень логирования: консоль={console_level}, файл={file_level if file_enabled else 'отключено'}")
    
    return logger

# Первоначальная инициализация логгера с дефолтными настройками
logger = configure_logger(None)

def update_logger_config(config_data: dict):
    """
    Обновляет конфигурацию логгера на основе переданных настроек.
    Вызывается из settings.py после загрузки конфигурации.
    """
    global logger
    logger = configure_logger(config_data)
    logger.debug("Настройки логгера обновлены из конфигурационного файла")

# Вспомогательная функция для логирования времени выполнения
def log_execution_time(func):
    """Декоратор для логирования времени выполнения функции"""
    import time
    from functools import wraps
    
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        logger.debug(f"Начало выполнения {func.__name__}")
        result = func(*args, **kwargs)
        execution_time = time.time() - start_time
        logger.debug(f"Функция {func.__name__} выполнена за {execution_time:.3f} сек")
        return result
    return wrapper