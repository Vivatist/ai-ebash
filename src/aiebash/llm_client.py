"""
Клиент для работы с LLM API через OpenRouter.

Поддерживает:
- Обычный режим запросов с ожиданием полного ответа
- Потоковый режим с отображением ответа в реальном времени
- Ленивую загрузку зависимостей для быстрого старта
- Markdown-форматирование ответов через Rich
"""
import threading
from typing import List, Dict, Optional
import time
from aiebash.formatter_text import format_api_key_display
from aiebash.i18n import t
from aiebash.logger import log_execution_time
from aiebash.config_manager import config

class _LazyImports:
    """Класс для ленивого импорта тяжелых зависимостей."""
    
    def __init__(self):
        self._console = None
        self._markdown = None
        self._live = None
        self._openai_client = None
    
    def get_console(self):
        """Возвращает экземпляр Rich Console."""
        if self._console is None:
            from rich.console import Console
            self._console = Console()
        return self._console
    
    def get_markdown(self):
        """Возвращает класс Rich Markdown."""
        if self._markdown is None:
            from rich.markdown import Markdown
            self._markdown = Markdown
        return self._markdown
    
    def get_live(self):
        """Возвращает класс Rich Live."""
        if self._live is None:
            from rich.live import Live
            self._live = Live
        return self._live
    
    def get_openai_client(self):
        """Возвращает класс OpenAI клиента."""
        if self._openai_client is None:
            from openai import OpenAI
            self._openai_client = OpenAI
        return self._openai_client


# Глобальный экземпляр для ленивых импортов
_imports = _LazyImports()


class OpenRouterClient:
    """Клиент для взаимодействия с LLM API через OpenRouter."""
    
    DEFAULT_TEMPERATURE = 0.7
    SPINNER_SLEEP_INTERVAL = 0.1

    def _spinner(self, stop_spinner: threading.Event) -> None:
        """Показывает спиннер во время ожидания ответа от AI.
        
        Args:
            stop_spinner: Event для остановки спиннера
        """
        console = _imports.get_console()
        status_text = "[dim]" + t('Ai thinking...') + "[/dim]"
        
        with console.status(status_text, spinner="dots", spinner_style="dim"):
            while not stop_spinner.is_set():
                time.sleep(self.SPINNER_SLEEP_INTERVAL)

    @log_execution_time
    def __init__(self, console, logger, api_key: str, api_url: str, model: str,
                 system_content: str, temperature: float = DEFAULT_TEMPERATURE):
        """Инициализирует клиент OpenRouter.
        
        Args:
            console: Rich консоль для вывода
            logger: Логгер для записи событий
            api_key: API ключ для авторизации
            api_url: URL API эндпоинта
            model: Название модели для использования
            system_content: Системное сообщение для контекста
            temperature: Параметр креативности модели (0.0-1.0)
        """
        self.console = console
        self.logger = logger
        self.api_key = api_key
        self.api_url = api_url
        self.model = model
        self.temperature = temperature
        self.messages: List[Dict[str, str]] = [
            {"role": "system", "content": system_content}
        ]
        self._client = None  # Ленивая инициализация

    @property
    def client(self):
        """Ленивая инициализация OpenAI клиента.
        
        Returns:
            Экземпляр OpenAI клиента
        """
        if self._client is None:
            openai_class = _imports.get_openai_client()
            self._client = openai_class(api_key=self.api_key, base_url=self.api_url)
        return self._client

    @log_execution_time
    def ask(self, user_input: str, educational_content: Optional[List[Dict[str, str]]] = None) -> str:
        """Отправляет запрос в обычном режиме и возвращает полный ответ.
        
        Args:
            user_input: Текст запроса пользователя
            educational_content: Дополнительные сообщения для контекста
            
        Returns:
            Полный ответ от AI модели
        """
        if educational_content is None:
            educational_content = []
            
        self._add_messages_to_context(educational_content, user_input)
        
        # Показ спиннера в отдельном потоке
        stop_spinner = threading.Event()
        spinner_thread = threading.Thread(target=self._spinner, args=(stop_spinner,))
        spinner_thread.start()

        try:
            response = self._make_api_request()
            reply = response.choices[0].message.content

            # Останавливаем спиннер
            stop_spinner.set()
            spinner_thread.join()

            self.messages.append({"role": "assistant", "content": reply})
            return reply

        except Exception:
            # Останавливаем спиннер
            stop_spinner.set()
            spinner_thread.join()
            raise

    def _add_messages_to_context(self, educational_content: List[Dict[str, str]], user_input: str) -> None:
        """Добавляет сообщения в контекст разговора."""
        self.messages.extend(educational_content)
        self.messages.append({"role": "user", "content": user_input})

    def _make_api_request(self):
        """Выполняет API запрос к модели."""
        return self.client.chat.completions.create(
            model=self.model,
            messages=self.messages,
            temperature=self.temperature
        )


    @log_execution_time
    def ask_stream(self, user_input: str, educational_content: Optional[List[Dict[str, str]]] = None) -> str:
        """Отправляет запрос в потоковом режиме с отображением ответа в реальном времени.
        
        Args:
            user_input: Текст запроса пользователя
            educational_content: Дополнительные сообщения для контекста
            
        Returns:
            Полный ответ от AI модели
        """
        if educational_content is None:
            educational_content = []
            
        self._add_messages_to_context(educational_content, user_input)
        reply_parts = []
        
        # Показ спиннера в отдельном потоке
        stop_spinner = threading.Event()
        spinner_thread = threading.Thread(target=self._spinner, args=(stop_spinner,))
        spinner_thread.start()
        
        try:
            stream = self._make_streaming_api_request()
            first_chunk = self._get_first_content_chunk(stream, reply_parts)
            
            # Останавливаем спиннер после получения первого чанка
            stop_spinner.set()
            if spinner_thread.is_alive():
                spinner_thread.join()

            if first_chunk:
                self._process_streaming_response(stream, reply_parts, first_chunk)
                
            reply = "".join(reply_parts)
            self.messages.append({"role": "assistant", "content": reply})
            return reply

        except Exception:
            # Останавливаем спиннер в случае ошибки
            stop_spinner.set()
            if spinner_thread.is_alive():
                spinner_thread.join()
            raise

    def _make_streaming_api_request(self):
        """Выполняет потоковый API запрос."""
        return self.client.chat.completions.create(
            model=self.model,
            messages=self.messages,
            temperature=self.temperature,
            stream=True
        )

    def _get_first_content_chunk(self, stream, reply_parts: List[str]) -> Optional[str]:
        """Получает первый чанк с контентом из потока."""
        for chunk in stream:
            if chunk.choices[0].delta.content:
                first_chunk = chunk.choices[0].delta.content
                reply_parts.append(first_chunk)
                return first_chunk
        return None

    def _process_streaming_response(self, stream, reply_parts: List[str], first_chunk: str) -> None:
        """Обрабатывает потоковый ответ с отображением через Rich Live."""
        sleep_time = config.get("global", "sleep_time", 0.01)
        live_class = _imports.get_live()
        markdown_class = _imports.get_markdown()
        
        with live_class(
            console=self.console,
            auto_refresh=False,
            refresh_per_second=1
        ) as live:
            # Показываем первый чанк
            if first_chunk:
                markdown = markdown_class(first_chunk)
                live.update(markdown)
                live.refresh()
            
            # Обрабатываем остальные чанки
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    text = chunk.choices[0].delta.content
                    reply_parts.append(text)
                    
                    full_text = "".join(reply_parts)
                    markdown = markdown_class(full_text)
                    live.update(markdown)
                    live.refresh()
                    time.sleep(sleep_time)
  


    def __str__(self) -> str:
        """Человекочитаемое представление клиента со всеми полями.

        Примечание: значение `api_key` маскируется (видны только последние 4 символа),
        а сложные объекты выводятся кратко.
        """

        items = {}
        for k, v in self.__dict__.items():
            if k == 'api_key':
                items[k] = format_api_key_display(v)
            elif k == 'messages' or k == 'console' or k == '_client' or k == 'logger':
                continue
            else:
                try:
                    items[k] = v
                except Exception:
                    items[k] = f"<unrepr {type(v).__name__}>"

        parts = [f"{self.__class__.__name__}("]
        for key, val in items.items():
            parts.append(f"  {key}={val!r},")
        parts.append(")")
        return "\n".join(parts)
