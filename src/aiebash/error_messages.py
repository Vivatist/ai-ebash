#!/usr/bin/env python3
"""
Обработка ошибок API с локализацией и ленивыми импортами.

ОСОБЕННОСТИ:
- Ленивая загрузка OpenAI исключений
- Локализованные сообщения об ошибках
- Маппинг различных типов ошибок API
- Поддержка ссылок на документацию
"""

from typing import Dict, Type, Optional
from aiebash.i18n import t


class ErrorMessageError(Exception):
    """Исключение для ошибок обработки сообщений об ошибках."""
    pass


class _LazyOpenAIImports:
    """Класс для ленивой загрузки OpenAI исключений."""
    
    def __init__(self):
        self._exceptions: Optional[Dict[str, Type[Exception]]] = None
        self._import_attempted = False
    
    def get_exceptions(self) -> Dict[str, Type[Exception]]:
        """Возвращает словарь OpenAI исключений с ленивой загрузкой."""
        if self._exceptions is None and not self._import_attempted:
            self._import_attempted = True
            try:
                from openai import (
                    RateLimitError, APIError, OpenAIError, AuthenticationError,
                    APIConnectionError, PermissionDeniedError, NotFoundError, BadRequestError
                )
                self._exceptions = {
                    'RateLimitError': RateLimitError,
                    'APIError': APIError,
                    'OpenAIError': OpenAIError,
                    'AuthenticationError': AuthenticationError,
                    'APIConnectionError': APIConnectionError,
                    'PermissionDeniedError': PermissionDeniedError,
                    'NotFoundError': NotFoundError,
                    'BadRequestError': BadRequestError
                }
            except ImportError as e:
                raise ErrorMessageError(f"Не удалось импортировать OpenAI исключения: {e}")
        
        if self._exceptions is None:
            raise ErrorMessageError("OpenAI исключения недоступны")
        
        return self._exceptions
    
    def is_instance(self, exception: Exception, exception_name: str) -> bool:
        """Проверяет, является ли исключение экземпляром указанного типа."""
        try:
            exceptions = self.get_exceptions()
            exception_type = exceptions.get(exception_name)
            if exception_type is None:
                return False
            return isinstance(exception, exception_type)
        except ErrorMessageError:
            return False


# Глобальный экземпляр для ленивых импортов
_openai_imports = _LazyOpenAIImports()


def _get_openai_exceptions():
    """Обратная совместимость со старым API."""
    return _openai_imports.get_exceptions()


def _extract_error_message(error: Exception) -> str:
    """Извлекает сообщение об ошибке из различных типов исключений."""
    try:
        # Пробуем получить сообщение из body атрибута (OpenAI API)
        body = getattr(error, 'body', None)
        if isinstance(body, dict) and 'message' in body:
            return body['message']
        
        # Возвращаем строковое представление ошибки
        return str(error)
    
    except Exception:
        return str(error)


def _get_documentation_url() -> str:
    """Возвращает URL документации."""
    return (
        "https://github.com/Vivatist/ai-ebash/blob/main/docs/locales/"
        "README_ru.md#%D0%BF%D0%BE%D0%BB%D1%83%D1%87%D0%B5%D0%BD%D0%B8%D0%B5-"
        "%D1%82%D0%BE%D0%BA%D0%B5%D0%BD%D0%B0-api_key-%D0%B8-%D0%BF%D0%BE%D0%B4"
        "%D0%BA%D0%BB%D1%8E%D1%87%D0%B5%D0%BD%D0%B8%D0%B5-%D0%BA-%D0%BF%D1%80%D0%B5"
        "%D0%B4%D1%83%D1%81%D1%82%D0%B0%D0%BD%D0%BE%D0%B2%D0%BB%D0%B5%D0%BD%D0%BD%D0%BE"
        "%D0%B9-%D0%BD%D0%B5%D0%B9%D1%80%D0%BE%D1%81%D0%B5%D1%82%D0%B8"
    )


def connection_error(error: Exception) -> str:
    """
    Преобразует API ошибки в локализованные сообщения.
    
    Args:
        error: Исключение для обработки
    
    Returns:
        str: Локализованное сообщение об ошибке
    """
    try:
        msg = _extract_error_message(error)
        doc_url = _get_documentation_url()
        
        # Проверяем типы ошибок через ленивые импорты
        if _openai_imports.is_instance(error, 'RateLimitError'):
            return t("[dim]Error 429: Exceeding the quota. Message from the provider: {message}. "
                    "You can change LLM in settings: 'ai --settings'[/dim]").format(message=msg)
        
        elif _openai_imports.is_instance(error, 'BadRequestError'):
            return t("[dim]Error 400: {message}. Check model name.[/dim]").format(message=msg)
        
        elif _openai_imports.is_instance(error, 'AuthenticationError'):
            return t("[dim]Error 401: Authentication failed. Check your API_KEY. "
                    "[link={link}]How to get a key?[/link][/dim]").format(link=doc_url)
        
        elif _openai_imports.is_instance(error, 'APIConnectionError'):
            return t("[dim]No connection, please check your Internet connection[/dim]")
        
        elif _openai_imports.is_instance(error, 'PermissionDeniedError'):
            return t("[dim]Error 403: Your region is not supported. Use VPN or change the LLM. "
                    "You can change LLM in settings: 'ai --settings'[/dim]")
        
        elif _openai_imports.is_instance(error, 'NotFoundError'):
            return t("[dim]Error 404: Resource not found. Check API_URL and Model in settings.[/dim]")
        
        elif _openai_imports.is_instance(error, 'APIError'):
            return t("[dim]Error API: {error}. Check the LLM settings, there may be an incorrect API_URL[/dim]").format(error=error)
        
        elif _openai_imports.is_instance(error, 'OpenAIError'):
            return t("[dim]Please check your API_KEY. See provider docs for obtaining a key. "
                    "[link={link}]How to get a key?[/link][/dim]").format(link=doc_url)
        
        else:
            return t("[dim]Unknown error: {error}[/dim]").format(error=error)
    
    except Exception as e:
        # Fallback при критических ошибках
        return t("[dim]Error processing error message: {error}[/dim]").format(error=str(e))


def is_retriable_error(error: Exception) -> bool:
    """
    Определяет, можно ли повторить запрос при данной ошибке.
    
    Args:
        error: Исключение для проверки
    
    Returns:
        bool: True если ошибка позволяет повтор
    """
    # Ошибки сети и временные проблемы сервера
    if _openai_imports.is_instance(error, 'APIConnectionError'):
        return True
    
    # Rate limiting - можно повторить с задержкой
    if _openai_imports.is_instance(error, 'RateLimitError'):
        return True
    
    # Проблемы аутентификации и авторизации - не повторять
    if _openai_imports.is_instance(error, 'AuthenticationError'):
        return False
    
    if _openai_imports.is_instance(error, 'PermissionDeniedError'):
        return False
    
    # Неверные запросы - не повторять
    if _openai_imports.is_instance(error, 'BadRequestError'):
        return False
    
    # Ресурс не найден - не повторять
    if _openai_imports.is_instance(error, 'NotFoundError'):
        return False
    
    # Остальные ошибки API - повторить можно
    if _openai_imports.is_instance(error, 'APIError'):
        return True
    
    # Для неизвестных ошибок не рекомендуем повтор
    return False
