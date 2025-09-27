#!/usr/bin/env python3
"""
Главный модуль приложения ai-ebash.

ОСОБЕННОСТИ:
- Ленивая загрузка всех тяжелых компонентов для быстрого старта
- Модульная архитектура с четким разделением ответственности
- Поддержка диалогового и одиночного режимов запросов
- Интеграция с различными LLM провайдерами через OpenRouter
- Обработка блоков кода с возможностью выполнения
"""

import sys
from pathlib import Path
from typing import Optional, List, Dict, Any
from abc import ABC, abstractmethod

# Добавляем parent (src) в sys.path для локального запуска
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

# Сначала импортируем настройки без импорта логгера
from aiebash.config_manager import config


class AppError(Exception):
    """Базовое исключение для ошибок приложения."""
    pass


class LazyImportError(AppError):
    """Ошибка ленивого импорта модулей."""
    pass


class LazyLogger:
    """
    Ленивый логгер с отложенной инициализацией для быстрого старта.
    
    Загружает реальный логгер только при первом обращении к методам логирования.
    """
    
    def __init__(self):
        self._logger = None
        self._initialized = False
    
    def _ensure_logger(self):
        """Обеспечивает инициализацию логгера."""
        if not self._initialized:
            try:
                from aiebash.logger import configure_logger
                self._logger = configure_logger(config.get("logging"))
                self._initialized = True
            except Exception as e:
                # Fallback к print при критических ошибках логгера
                print(f"⚠️ Logger initialization failed: {e}")
                self._logger = None
                self._initialized = True
    
    def info(self, msg: str) -> None:
        """Логирует информационное сообщение."""
        self._ensure_logger()
        if self._logger:
            self._logger.info(msg)
        else:
            print(f"INFO: {msg}")
    
    def debug(self, msg: str) -> None:
        """Логирует отладочное сообщение."""
        self._ensure_logger()
        if self._logger:
            self._logger.debug(msg)
    
    def error(self, msg: str) -> None:
        """Логирует ошибку."""
        self._ensure_logger()
        if self._logger:
            self._logger.error(msg)
        else:
            print(f"ERROR: {msg}")
    
    def critical(self, msg: str, exc_info: Optional[bool] = None) -> None:
        """Логирует критическую ошибку."""
        self._ensure_logger()
        if self._logger:
            self._logger.critical(msg, exc_info=exc_info)
        else:
            print(f"CRITICAL: {msg}")


# Глобальный экземпляр ленивого логгера
logger = LazyLogger()

class LazyImportManager:
    """
    Менеджер для ленивой загрузки тяжелых модулей и компонентов.
    
    Обеспечивает быстрый старт приложения путем отложенной загрузки
    больших библиотек до момента их фактического использования.
    """
    
    def __init__(self):
        # Состояние импортов
        self._i18n_initialized = False
        self._prompt_toolkit_imported = False
        
        # Кэш импортированных модулей
        self._rich_console = None
        self._script_executor = None
        self._formatter_text = None
        self._markdown = None
        
        # i18n компоненты
        self._translator = None
        self._t_function = None
        
        # prompt_toolkit компоненты
        self._html = None
        self._prompt = None
        self._file_history = None
        self._style = None
    
    def ensure_i18n(self):
        """Обеспечивает инициализацию системы интернационализации."""
        if not self._i18n_initialized:
            try:
                from aiebash.i18n import t, translator
                self._t_function = t
                self._translator = translator
                
                # Инициализируем язык из конфигурации
                try:
                    language = getattr(config, 'language', 'en')
                    translator.set_language(language)
                except Exception as e:
                    logger.debug(f"Failed to set language: {e}")
                
                self._i18n_initialized = True
            except ImportError as e:
                raise LazyImportError(f"Failed to import i18n: {e}")
    
    def get_t_function(self):
        """Возвращает функцию перевода с ленивой инициализацией."""
        self.ensure_i18n()
        return self._t_function
    
    def ensure_prompt_toolkit(self):
        """Обеспечивает импорт prompt_toolkit компонентов."""
        if not self._prompt_toolkit_imported:
            try:
                from prompt_toolkit import HTML, prompt
                from prompt_toolkit.history import FileHistory
                from prompt_toolkit.styles import Style
                
                self._html = HTML
                self._prompt = prompt
                self._file_history = FileHistory
                self._style = Style
                
                self._prompt_toolkit_imported = True
            except ImportError as e:
                raise LazyImportError(f"Failed to import prompt_toolkit: {e}")
    
    def get_rich_console(self):
        """Возвращает класс Rich Console с ленивой загрузкой."""
        if self._rich_console is None:
            try:
                from rich.console import Console
                self._rich_console = Console
            except ImportError as e:
                raise LazyImportError(f"Failed to import Rich Console: {e}")
        return self._rich_console
    
    def get_script_executor(self):
        """Возвращает функцию выполнения скриптов с ленивой загрузкой."""
        if self._script_executor is None:
            try:
                from aiebash.script_executor import run_code_block
                self._script_executor = run_code_block
            except ImportError as e:
                raise LazyImportError(f"Failed to import script_executor: {e}")
        return self._script_executor
    
    def get_formatter_text(self):
        """Возвращает функцию форматирования текста с ленивой загрузкой."""
        if self._formatter_text is None:
            try:
                from aiebash.formatter_text import extract_labeled_code_blocks
                self._formatter_text = extract_labeled_code_blocks
            except ImportError as e:
                raise LazyImportError(f"Failed to import formatter_text: {e}")
        return self._formatter_text
    
    def get_markdown(self):
        """Возвращает класс Markdown с ленивой загрузкой."""
        if self._markdown is None:
            try:
                from rich.markdown import Markdown
                self._markdown = Markdown
            except ImportError as e:
                raise LazyImportError(f"Failed to import Rich Markdown: {e}")
        return self._markdown
    
    def get_prompt_toolkit_components(self):
        """Возвращает все компоненты prompt_toolkit."""
        self.ensure_prompt_toolkit()
        return {
            'HTML': self._html,
            'prompt': self._prompt,
            'FileHistory': self._file_history,
            'Style': self._style
        }


# Глобальный менеджер ленивых импортов
import_manager = LazyImportManager()


def log_execution_time(func):
    """Простой декоратор времени выполнения (отключен для ускорения)."""
    return func  # Временно отключаем для ускорения загрузки


def t_lazy(text, **kwargs):
    """Ленивая загрузка функции перевода."""
    t_func = import_manager.get_t_function()
    return t_func(text, **kwargs)


# Псевдоним для удобства использования
t = t_lazy



class AppConfig:
    """
    Класс для управления конфигурацией приложения.
    
    Централизует доступ к настройкам и обеспечивает их валидацию.
    """
    
    def __init__(self):
        self._stream_output_mode = None
        self._educational_content = None
    
    @property
    def stream_output_mode(self) -> bool:
        """Режим потокового вывода."""
        if self._stream_output_mode is None:
            self._stream_output_mode = config.get("global", "stream_output_mode", False)
            logger.info(f"Settings - Stream output mode: {self._stream_output_mode}")
        return self._stream_output_mode
    
    @property
    def educational_content(self) -> List[Dict[str, str]]:
        """Образовательный контент для LLM."""
        if self._educational_content is None:
            educational_text = (
                "ALWAYS number code blocks in your replies so the user can reference them. "
                "Numbering format: [Code #1]\n```bash ... ```, [Code #2]\n```bash ... ```, "
                "etc. Insert the numbering BEFORE the block "
                "If there are multiple code blocks, number them sequentially. "
                "In each new reply, start numbering from 1 again. Do not discuss numbering; just do it automatically."
            )
            self._educational_content = [{'role': 'user', 'content': educational_text}]
        return self._educational_content.copy()
    
    def get_system_content(self) -> str:
        """Создает системный контент для LLM."""
        user_content = config.get("global", "user_content", "")
        json_mode = config.get("global", "json_mode", False)

        additional_content_json = ""
        if json_mode:
            additional_content_json = (
                "You must always respond with a single JSON object containing fields 'cmd' and 'info'. "
            )

        # Базовая информация без вызова медленной системной информации
        additional_content_main = (
            "Your name is Ai-eBash, a sysadmin assistant. "
            "You and the user always work in a terminal. "
            "Respond based on the user's environment and commands. "
        )
        
        system_content = f"{user_content} {additional_content_json} {additional_content_main}".strip()
        return system_content
    
    def get_llm_config(self) -> Dict[str, Any]:
        """Возвращает конфигурацию текущей LLM."""
        return config.get_current_llm_config()


# Глобальная конфигурация приложения
app_config = AppConfig()

# Импортируем только самое необходимое для быстрого старта
from aiebash.llm_client import OpenRouterClient
from aiebash.arguments import parse_args
from aiebash.error_messages import connection_error

class QueryExecutor:
    """
    Класс для выполнения запросов к LLM в различных режимах.
    
    Поддерживает как одиночные запросы, так и интерактивный диалог.
    """
    
    def __init__(self, chat_client: OpenRouterClient, console, import_manager: LazyImportManager):
        self.chat_client = chat_client
        self.console = console
        self.import_manager = import_manager
    
    @log_execution_time
    def run_single_query(self, query: str) -> None:
        """
        Выполняет одиночный запрос к LLM.
        
        Args:
            query: Текст запроса к LLM
        """
        logger.info(f"Running single query: '{query[:50]}'...")
        
        try:
            if app_config.stream_output_mode:
                reply = self.chat_client.ask_stream(query)
            else:
                reply = self.chat_client.ask(query)
                markdown_class = self.import_manager.get_markdown()
                self.console.print(markdown_class(reply))
        except Exception as e:
            self.console.print(connection_error(e))
            logger.error(f"Connection error in single query: {e}")
    
    @log_execution_time
    def run_dialog_mode(self, initial_user_prompt: Optional[str] = None) -> None:
        """
        Запускает интерактивный режим диалога с LLM.
        
        Args:
            initial_user_prompt: Опциональный начальный запрос
        """
        logger.info("Starting dialog mode")
        
        try:
            # Получаем компоненты prompt_toolkit
            pt_components = self.import_manager.get_prompt_toolkit_components()
            
            # История команд
            history_file_path = config.user_config_dir / "cmd_history"
            history = pt_components['FileHistory'](str(history_file_path))
            
            # Образовательный контент (изменяемая копия)
            educational_content = app_config.educational_content
            last_code_blocks = []
            
            # Обработка начального запроса
            if initial_user_prompt:
                reply = self._process_user_input(
                    initial_user_prompt, educational_content
                )
                if reply:
                    last_code_blocks = self._extract_code_blocks(reply)
                    educational_content.clear()  # Очищаем после первого использования
                self.console.print()
            
            # Основной цикл диалога
            self._dialog_loop(pt_components, history, educational_content, last_code_blocks)
        
        except Exception as e:
            logger.error(f"Error in dialog mode: {e}")
            self.console.print(f"[red]Dialog mode error: {e}[/red]")
    
    def _process_user_input(self, user_input: str, educational_content: List[Dict[str, str]]) -> Optional[str]:
        """
        Обрабатывает пользовательский ввод и отправляет запрос к LLM.
        
        Returns:
            Ответ от LLM или None в случае ошибки
        """
        try:
            markdown_class = self.import_manager.get_markdown()
            
            if app_config.stream_output_mode:
                reply = self.chat_client.ask_stream(user_input, educational_content=educational_content)
                return reply
            else:
                reply = self.chat_client.ask(user_input, educational_content=educational_content)
                self.console.print(markdown_class(reply))
                return reply
        
        except Exception as e:
            self.console.print(connection_error(e))
            logger.error(f"Connection error: {e}")
            return None
    
    def _extract_code_blocks(self, text: str) -> List[Any]:
        """Извлекает блоки кода из текста ответа LLM."""
        try:
            formatter_func = self.import_manager.get_formatter_text()
            return formatter_func(text)
        except Exception as e:
            logger.error(f"Error extracting code blocks: {e}")
            return []
    
    def _execute_code_block(self, last_code_blocks: List[Any], block_index: int) -> bool:
        """
        Выполняет блок кода по индексу.
        
        Returns:
            True если блок был выполнен успешно, False иначе
        """
        try:
            if 1 <= block_index <= len(last_code_blocks):
                executor_func = self.import_manager.get_script_executor()
                executor_func(self.console, last_code_blocks, block_index)
                return True
            else:
                self.console.print(f"[dim]Code block #{block_index} not found.[/dim]")
                return False
        except Exception as e:
            logger.error(f"Error executing code block {block_index}: {e}")
            self.console.print(f"[red]Error executing code block: {e}[/red]")
            return False
    
    def _dialog_loop(self, pt_components, history, educational_content: List[Dict[str, str]], last_code_blocks: List[Any]) -> None:
        """Основной цикл интерактивного диалога."""
        while True:
            try:
                # Настройка стилей промпта
                style = pt_components['Style'].from_dict({
                    "prompt": "bold fg:green",
                })
                
                # Выбор placeholder в зависимости от наличия блоков кода
                if last_code_blocks:
                    placeholder_text = "<i><gray>The number of the code block to execute or the next question... Ctrl+C - exit</gray></i>"
                else:
                    placeholder_text = "<i><gray>Your question... Ctrl+C - exit</gray></i>"
                
                placeholder = pt_components['HTML'](t(placeholder_text))
                
                # Получение пользовательского ввода
                user_prompt = pt_components['prompt'](
                    [("class:prompt", ">>> ")],
                    placeholder=placeholder,
                    history=history,
                    style=style,
                    multiline=False,
                    wrap_lines=True,
                    enable_history_search=True
                )
                
                # Обработка пустого ввода
                if not user_prompt:
                    continue
                
                # Команды выхода
                if user_prompt.lower() in ['exit', 'quit', 'q']:
                    break
                
                # Выполнение блока кода по номеру
                if user_prompt.isdigit():
                    block_index = int(user_prompt)
                    self._execute_code_block(last_code_blocks, block_index)
                    self.console.print()
                    continue
                
                # Обычный запрос к LLM
                reply = self._process_user_input(user_prompt, educational_content)
                if reply:
                    educational_content.clear()  # Очищаем после использования
                    last_code_blocks = self._extract_code_blocks(reply)
                self.console.print()  # Новая строка после ответа
            
            except KeyboardInterrupt:
                logger.info("Dialog interrupted by user")
                break
            except Exception as e:
                self.console.print(connection_error(e))
                logger.error(f"Dialog loop error: {e}")


class LLMClientFactory:
    """
    Фабрика для создания клиентов LLM с ленивой инициализацией.
    
    Обеспечивает создание правильно сконфигурированных клиентов
    только когда они действительно нужны.
    """
    
    @staticmethod
    def create_openrouter_client(console, import_manager: LazyImportManager) -> OpenRouterClient:
        """
        Создает клиент OpenRouter с текущей конфигурацией.
        
        Args:
            console: Rich консоль для вывода
            import_manager: Менеджер ленивых импортов
        
        Returns:
            Настроенный клиент OpenRouterClient
        
        Raises:
            AppError: При ошибке конфигурации LLM
        """
        logger.info("Initializing OpenRouter client")
        
        try:
            llm_config = app_config.get_llm_config()
            
            # Проверяем наличие необходимых параметров
            required_keys = ["api_key", "api_url", "model"]
            missing_keys = [key for key in required_keys if not llm_config.get(key)]
            
            if missing_keys:
                raise AppError(f"Missing LLM configuration: {', '.join(missing_keys)}")
            
            chat_client = OpenRouterClient(
                console=console,
                logger=logger,
                api_key=llm_config["api_key"],
                api_url=llm_config["api_url"],
                model=llm_config["model"],
                system_content=app_config.get_system_content(),
                temperature=config.get("global", "temperature", 0.7)
            )
            
            logger.info(f"OpenRouter client created successfully: {chat_client}")
            return chat_client
        
        except Exception as e:
            logger.error(f"Failed to create OpenRouter client: {e}")
            raise AppError(f"Failed to create LLM client: {e}")


class Application:
    """
    Главный класс приложения ai-ebash.
    
    Управляет жизненным циклом приложения, обрабатывает аргументы командной строки
    и координирует работу различных компонентов.
    """
    
    def __init__(self):
        self.import_manager = import_manager
        self.console = None
        self.chat_client = None
        self.query_executor = None
    
    def _initialize_console(self):
        """Инициализирует Rich консоль."""
        if self.console is None:
            try:
                console_class = self.import_manager.get_rich_console()
                self.console = console_class()
                logger.debug("Rich console initialized")
            except LazyImportError as e:
                logger.error(f"Failed to initialize console: {e}")
                raise AppError(f"Console initialization failed: {e}")
    
    def _initialize_llm_client(self):
        """Инициализирует LLM клиент."""
        if self.chat_client is None:
            self._initialize_console()
            self.chat_client = LLMClientFactory.create_openrouter_client(
                self.console, self.import_manager
            )
    
    def _initialize_query_executor(self):
        """Инициализирует исполнитель запросов."""
        if self.query_executor is None:
            self._initialize_llm_client()
            self.query_executor = QueryExecutor(
                self.chat_client, self.console, self.import_manager
            )
    
    def run_settings_mode(self) -> int:
        """
        Запускает режим настроек.
        
        Returns:
            Код возврата (0 для успеха)
        """
        logger.info("Starting configuration mode")
        
        try:
            from aiebash.config_menu import main_menu
            main_menu()
            logger.info("Configuration mode finished successfully")
            return 0
        except Exception as e:
            logger.error(f"Configuration mode error: {e}")
            print(f"❌ Settings mode failed: {e}")
            return 1
    
    def run_ai_mode(self, dialog_mode: bool, prompt: str) -> int:
        """
        Запускает AI режим (диалоговый или одиночный запрос).
        
        Args:
            dialog_mode: Флаг диалогового режима
            prompt: Текст запроса (для одиночного режима)
        
        Returns:
            Код возврата (0 для успеха)
        """
        try:
            self._initialize_query_executor()
            
            if dialog_mode or not prompt:
                # Диалоговый режим
                logger.info("Starting in dialog mode")
                self.query_executor.run_dialog_mode(
                    initial_user_prompt=prompt if prompt else None
                )
            else:
                # Режим одиночного запроса
                logger.info("Starting in single-query mode")
                self.query_executor.run_single_query(prompt)
            
            return 0
        
        except AppError as e:
            logger.error(f"AI mode error: {e}")
            if self.console:
                self.console.print(f"[red]Error: {e}[/red]")
            else:
                print(f"❌ Error: {e}")
            return 1
        except Exception as e:
            logger.critical(f"Unexpected error in AI mode: {e}", exc_info=True)
            if self.console:
                self.console.print(f"[red]Unexpected error: {e}[/red]")
            else:
                print(f"❌ Unexpected error: {e}")
            return 1
    
    @log_execution_time
    def run(self) -> int:
        """
        Главный метод запуска приложения.
        
        Returns:
            Код возврата программы
        """
        try:
            # Парсинг аргументов командной строки
            args = parse_args()
            
            # Режим настроек
            if args.settings:
                return self.run_settings_mode()
            
            # AI режим
            dialog_mode = args.dialog
            prompt_parts = args.prompt or []
            prompt = " ".join(prompt_parts).strip()
            
            return self.run_ai_mode(dialog_mode, prompt)
        
        except KeyboardInterrupt:
            logger.info("Application interrupted by user")
            return 130
        except Exception as e:
            logger.critical(f"Unhandled application error: {e}", exc_info=True)
            print(f"❌ Critical error: {e}")
            return 1
        finally:
            print()  # Печатаем пустую строку в любом случае


def main() -> int:
    """
    Точка входа в приложение.
    
    Returns:
        Код возврата программы
    """
    app = Application()
    exit_code = app.run()
    
    if exit_code == 0:
        logger.info("Program finished successfully")
    else:
        logger.info(f"Program finished with exit code: {exit_code}")
    
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
