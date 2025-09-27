#!/usr/bin/env python3
"""
Логгер с ленивыми импортами и Rich интеграцией.

ОСОБЕННОСТИ:
- Ленивая загрузка Rich компонентов для быстрого старта
- Поддержка вращения файлов логов
- Настраиваемые уровни для консоли и файлов
- Автоматическая конфигурация от настроек приложения
"""

import logging
import sys
import platform
from pathlib import Path
from typing import Dict, Any, Optional, Union
from logging.handlers import RotatingFileHandler
from platformdirs import user_config_dir


class LoggerError(Exception):
    """Исключение для ошибок логгера."""
    pass


class LogLevel:
    """Константы для уровней логирования."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class _LazyRichImports:
    """Класс для ленивой загрузки Rich компонентов."""
    
    def __init__(self):
        self._handler = None
        self._console = None
        self._traceback_installed = False
    
    @property
    def handler(self):
        """Ленивый импорт RichHandler."""
        if self._handler is None:
            try:
                from rich.logging import RichHandler
                self._handler = RichHandler
            except ImportError:
                raise LoggerError("Rich не установлен. Используйте pip install rich")
        return self._handler
    
    @property
    def console(self):
        """Ленивый импорт Rich Console."""
        if self._console is None:
            try:
                from rich.console import Console
                self._console = Console
            except ImportError:
                raise LoggerError("Rich не установлен. Используйте pip install rich")
        return self._console
    
    def install_traceback(self) -> None:
        """Ленивая установка Rich traceback."""
        if not self._traceback_installed:
            try:
                from rich.traceback import install
                install(show_locals=True)
                self._traceback_installed = True
            except ImportError:
                # Если Rich недоступен, просто игнорируем
                pass

# Константы
APP_NAME = "ai-ebash"
log_dir = Path(user_config_dir(APP_NAME)) / "logs"

# Создаем директорию для логов с обработкой ошибок
try:
    log_dir.mkdir(parents=True, exist_ok=True)
except Exception as e:
    print(f"⚠️ Не удалось создать директорию логов: {e}")
    # Используем временную директорию
    import tempfile
    log_dir = Path(tempfile.gettempdir()) / "ai-ebash-logs"
    log_dir.mkdir(exist_ok=True)

# Создаем глобальные объекты
_rich_imports = _LazyRichImports()

def get_log_level(level_name: Union[str, int]) -> int:
    """
    Преобразует строковое имя или число уровня логирования в константу logging.
    
    Args:
        level_name: Строковое имя уровня или числовое значение
    
    Returns:
        int: Числовое значение уровня логирования
    
    Raises:
        LoggerError: При неверном уровне логирования
    """
    if isinstance(level_name, int):
        return level_name
    
    if not isinstance(level_name, str):
        raise LoggerError(f"Неверный тип уровня логирования: {type(level_name)}")
    
    level_map = {
        LogLevel.DEBUG.lower(): logging.DEBUG,
        LogLevel.INFO.lower(): logging.INFO,
        LogLevel.WARNING.lower(): logging.WARNING,
        LogLevel.ERROR.lower(): logging.ERROR,
        LogLevel.CRITICAL.lower(): logging.CRITICAL
    }
    
    normalized_level = level_name.lower().strip()
    if normalized_level not in level_map:
        raise LoggerError(f"Неизвестный уровень логирования: {level_name}")
    
    return level_map[normalized_level]

class LoggerConfig:
    """Класс для конфигурации логгера."""
    
    def __init__(self, config_data: Optional[Dict] = None):
        self.log_level = logging.INFO
        self.console_level = logging.CRITICAL
        self.file_level = logging.DEBUG
        self.file_enabled = False
        self.file_max_bytes = 5 * 1024 * 1024  # 5MB
        self.file_backup_count = 3
        
        if config_data:
            self._apply_config(config_data)
    
    def _apply_config(self, config_data: Dict[str, Any]) -> None:
        """Применяет настройки из словаря конфигурации."""
        try:
            self.log_level = get_log_level(config_data.get('level', 'INFO'))
            self.console_level = get_log_level(config_data.get('console_level', 'CRITICAL'))
            self.file_level = get_log_level(config_data.get('file_level', 'DEBUG'))
            self.file_enabled = bool(config_data.get('file_enabled', False))
            self.file_max_bytes = int(config_data.get('file_max_bytes', 5 * 1024 * 1024))
            self.file_backup_count = int(config_data.get('file_backup_count', 3))
        except (ValueError, TypeError, LoggerError) as e:
            raise LoggerError(f"Ошибка конфигурации логгера: {e}")


def configure_logger(config_data: Optional[Dict] = None) -> logging.Logger:
    """
    Настраивает и возвращает логгер с указанными параметрами.
    
    Args:
        config_data: Настройки логирования из конфигурации
    
    Returns:
        logging.Logger: Настроенный логгер
    
    Raises:
        LoggerError: При ошибках конфигурации
    """
    global logger
    
    try:
        config = LoggerConfig(config_data)
        
        # Создаем новый логгер
        logger = logging.getLogger('ai-ebash')
        logger.setLevel(config.log_level)
        
        # Очистка существующих обработчиков
        if logger.hasHandlers():
            logger.handlers.clear()
        
        # Создаем ленивые импорты Rich
        rich_imports = _LazyRichImports()
        
        # Консольный вывод с ленивой загрузкой Rich
        try:
            console = rich_imports.console()
            console_handler = rich_imports.handler(
                console=console,
                rich_tracebacks=True,
                markup=True,
                show_path=False
            )
            console_handler.setLevel(config.console_level)
            logger.addHandler(console_handler)
            
            # Устанавливаем Rich traceback
            rich_imports.install_traceback()
            
        except LoggerError:
            # Fallback к стандартному StreamHandler если Rich недоступен
            console_handler = logging.StreamHandler()
            console_formatter = logging.Formatter(
                '%(asctime)s - %(levelname)s - %(message)s',
                datefmt='%H:%M:%S'
            )
            console_handler.setFormatter(console_formatter)
            console_handler.setLevel(config.console_level)
            logger.addHandler(console_handler)
        
        # Файловый вывод
        if config.file_enabled:
            try:
                file_formatter = logging.Formatter(
                    '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
                )
                file_handler = RotatingFileHandler(
                    log_dir / "ai-ebash.log",
                    maxBytes=config.file_max_bytes,
                    backupCount=config.file_backup_count,
                    encoding='utf-8'
                )
                file_handler.setLevel(config.file_level)
                file_handler.setFormatter(file_formatter)
                logger.addHandler(file_handler)
            except Exception as e:
                # Если не удается создать файловый обработчик, продолжаем без него
                logger.warning(f"Не удалось создать файловый обработчик: {e}")
        
        # Логируем системную информацию при запуске
        _log_system_info(logger, config)
        
        return logger
        
    except Exception as e:
        raise LoggerError(f"Ошибка настройки логгера: {e}")


def _log_system_info(logger_instance: logging.Logger, config: LoggerConfig) -> None:
    """Логирует информацию о системе при запуске."""
    try:
        logger_instance.info(f"Starting ai-ebash on {platform.system()} {platform.release()}")
        logger_instance.debug(f"Python {platform.python_version()}, interpreter: {sys.executable}")
        console_level_name = logging.getLevelName(config.console_level)
        file_level_info = logging.getLevelName(config.file_level) if config.file_enabled else 'disabled'
        logger_instance.debug(f"Log levels: console={console_level_name}, file={file_level_info}")
    except Exception:
        # Игнорируем ошибки логирования системной информации
        pass

def update_logger_config(config_data: Dict[str, Any]) -> None:
    """
    Обновляет конфигурацию логгера на основе переданных настроек.
    Вызывается из config_manager.py после загрузки конфигурации.
    
    Args:
        config_data: Словарь с настройками логирования
    """
    global logger
    try:
        logger = configure_logger(config_data)
        logger.debug("Logger settings updated from config file")
    except LoggerError as e:
        print(f"⚠️ Ошибка обновления настроек логгера: {e}")
        # Продолжаем с текущим логгером


def log_execution_time(func):
    """
    Декоратор для логирования времени выполнения функции.
    
    Args:
        func: Функция для декорирования
    
    Returns:
        Обернутая функция с логированием времени выполнения
    """
    import time
    from functools import wraps
    
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        try:
            result = func(*args, **kwargs)
            execution_time = time.perf_counter() - start_time
            logger.debug(f"Function '{func.__name__}' executed in {execution_time:.3f}s")
            return result
        except Exception as e:
            execution_time = time.perf_counter() - start_time
            logger.error(f"Function '{func.__name__}' failed after {execution_time:.3f}s: {e}")
            raise
    
    return wrapper


def get_logger_info() -> Dict[str, Any]:
    """
    Возвращает информацию о текущем состоянии логгера.
    
    Returns:
        Dict[str, Any]: Информация о логгере
    """
    try:
        current_logger = logging.getLogger('ai-ebash')
        return {
            "name": current_logger.name,
            "level": logging.getLevelName(current_logger.level),
            "handlers_count": len(current_logger.handlers),
            "log_dir": str(log_dir),
            "log_dir_exists": log_dir.exists(),
            "handlers": [
                {
                    "type": type(handler).__name__,
                    "level": logging.getLevelName(handler.level)
                }
                for handler in current_logger.handlers
            ]
        }
    except Exception as e:
        return {"error": str(e)}


# Первоначальная инициализация логгера с дефолтными настройками
try:
    logger = configure_logger(None)
except LoggerError as e:
    # Fallback к базовому логгеру при критических ошибках
    logger = logging.getLogger('ai-ebash')
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.error(f"Ошибка инициализации логгера: {e}")