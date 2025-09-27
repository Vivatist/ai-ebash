#!/usr/bin/env python3
"""
Привлекательный вывод текущих настроек приложения в консоль.

ВОЗМОЖНОСТИ:
- Отображение текущей LLM и её настроек
- Показ пользовательского контента и температуры
- Таблица всех добавленных LLM с отметкой текущей
- Информация об уровне логирования
- Поддержка как Rich, так и обычного вывода
- Локализация сообщений
"""

from typing import Optional, Dict, Any, List
from aiebash.config_manager import config
from aiebash.formatter_text import format_api_key_display
from aiebash.i18n import t


class SettingsOverviewError(Exception):
    """Исключение для ошибок отображения настроек."""
    pass


class _LazyRichImports:
    """Класс для ленивой загрузки Rich компонентов."""
    
    def __init__(self):
        self._console = None
        self._table = None
        self._panel = None
        self._text = None
        self._import_attempted = False
    
    def _try_import(self):
        """Попытка импорта Rich компонентов."""
        if not self._import_attempted:
            self._import_attempted = True
            try:
                from rich.console import Console
                from rich.table import Table
                from rich.panel import Panel
                from rich.text import Text
                
                self._console = Console
                self._table = Table
                self._panel = Panel
                self._text = Text
            except ImportError:
                pass
    
    @property
    def available(self) -> bool:
        """Проверяет, доступен ли Rich."""
        self._try_import()
        return self._console is not None
    
    @property
    def console(self):
        """Возвращает класс Console."""
        self._try_import()
        if self._console is None:
            raise SettingsOverviewError("Rich Console недоступен")
        return self._console
    
    @property
    def table(self):
        """Возвращает класс Table."""
        self._try_import()
        if self._table is None:
            raise SettingsOverviewError("Rich Table недоступен")
        return self._table
    
    @property
    def panel(self):
        """Возвращает класс Panel."""
        self._try_import()
        if self._panel is None:
            raise SettingsOverviewError("Rich Panel недоступен")
        return self._panel
    
    @property
    def text(self):
        """Возвращает класс Text."""
        self._try_import()
        if self._text is None:
            raise SettingsOverviewError("Rich Text недоступен")
        return self._text


# Глобальный экземпляр для ленивых импортов
_rich_imports = _LazyRichImports()


class SettingsData:
    """Класс для сбора и структурирования данных настроек."""
    
    def __init__(self):
        self.current_llm = config.current_llm or "(not selected)"
        self.current_config = config.get_current_llm_config() or {}
        self.user_content = config.user_content or t("(empty)")
        self.temperature = config.temperature
        self.available_llms = config.get_available_llms() or []
        self.console_log_level = config.console_log_level
        self.file_enabled = getattr(config, 'file_enabled', False)
        self.file_log_level = getattr(config, 'file_log_level', 'DEBUG')
    
    def get_current_llm_info(self) -> List[str]:
        """Возвращает информацию о текущей LLM."""
        lines = [f"{t('Name')}: {self.current_llm}"]
        
        if self.current_config:
            lines.extend([
                f"{t('Model')}: {self.current_config.get('model', '')}",
                f"API URL: {self.current_config.get('api_url', '')}",
                f"{t('API key')}: {format_api_key_display(self.current_config.get('api_key', ''))}"
            ])
        else:
            lines.append(t("No settings found"))
        
        return lines
    
    def get_content_info(self) -> List[str]:
        """Возвращает информацию о контенте и температуре."""
        lines = [t("Content") + ":"]
        
        if self.user_content and self.user_content != t("(empty)"):
            for line in str(self.user_content).splitlines() or [self.user_content]:
                lines.append(f"  {line}")
        else:
            lines.append(f"  {t('(empty)')}") 
        
        lines.append(f"\n{t('Temperature')}: {self.temperature}")
        return lines
    
    def get_logging_info(self) -> List[str]:
        """Возвращает информацию о логировании."""
        lines = [f"{t('Console log level')}: {self.console_log_level}"]
        
        if self.file_enabled:
            lines.append(f"{t('File logging')}: On ({self.file_log_level})")
        else:
            lines.append(f"{t('File logging')}: Off")
        
        return lines


def _plain_overview_print() -> None:
    """
    Выводит обзор настроек в обычном текстовом формате.
    
    Используется как fallback когда Rich недоступен.
    """
    try:
        data = SettingsData()
        
        print("=" * 60)
        print(t("Settings overview"))
        print("=" * 60)

        # Текущая LLM
        print("\n" + t("Current LLM") + ":")
        for line in data.get_current_llm_info():
            print(f"  {line}")

        # Контент и температура
        print("\n" + t("Content and temperature") + ":")
        for line in data.get_content_info():
            if line.startswith("  "):
                print(f"  {line}")
            else:
                print(f"  {line}")

        # Все LLM
        print("\n" + t("Available LLMs") + ":")
        if not data.available_llms:
            print("  " + t("No LLMs added"))
        else:
            _print_llms_table_plain(data)

        # Логирование
        print("\n" + t("Logging") + ":")
        for line in data.get_logging_info():
            print(f"  {line}")
        
        print("=" * 60)
    
    except Exception as e:
        print(f"⚠️ Ошибка при выводе настроек: {e}")
        _print_minimal_settings()


def _print_llms_table_plain(data: SettingsData) -> None:
    """Выводит таблицу LLM в текстовом формате."""
    header = f"{t('LLM'):20} | {t('Model'):20} | {'API URL':30} | {t('API key')}"
    print(header)
    print("-" * len(header))
    
    for name in data.available_llms:
        cfg = config.get_llm_config(name) or {}
        is_current = name == data.current_llm
        current_mark = " ✓" if is_current else "  "
        
        row = [
            f"{current_mark}{name}",
            cfg.get('model', '') or '',
            cfg.get('api_url', '') or '',
            format_api_key_display(cfg.get('api_key', '') or ''),
        ]
        print(f"{row[0]:20} | {row[1]:20} | {row[2]:30} | {row[3]}")


def _print_minimal_settings() -> None:
    """Минимальный вывод настроек при ошибках."""
    try:
        print("\n=== Базовые настройки ===")
        print(f"Текущая LLM: {config.current_llm or 'Не выбрана'}")
        print(f"Температура: {config.temperature}")
        print(f"Доступно LLM: {len(config.get_available_llms())}")
        print("===========================\n")
    except Exception:
        print("\n❌ Не удалось загрузить настройки\n")


def _print_rich_overview(console: Optional[object] = None) -> None:
    """
    Выводит обзор настроек используя Rich библиотеку.
    
    Args:
        console: Опционально переданный rich.Console для вывода
    """
    data = SettingsData()
    
    # Создаем или используем переданную консоль
    if console is None:
        console = _rich_imports.console()
    
    console.rule(t("Settings overview"))

    # Текущая LLM
    current_lines = []
    current_lines.append(t("Current LLM") + f": [bold]{data.current_llm}[/bold]")
    
    if data.current_config:
        current_lines.extend([
            f"{t('Model')}: {data.current_config.get('model', '')}",
            f"API URL: {data.current_config.get('api_url', '')}",
            f"{t('API key')}: {format_api_key_display(data.current_config.get('api_key', ''))}"
        ])
    else:
        current_lines.append(t("No settings found"))

    console.print(_rich_imports.panel.fit("\n".join(current_lines), title=t("Current LLM")))

    # Контент и температура
    content_lines = [t("Content") + ":"]
    if data.user_content and data.user_content != t("(empty)"):
        for line in str(data.user_content).splitlines() or [data.user_content]:
            content_lines.append(f"  {line}")
    else:
        content_lines.append(f"  {t('(empty)')}") 
    
    content_lines.append(f"\n{t('Temperature')}: [bold]{data.temperature}[/bold]")
    console.print(_rich_imports.panel.fit("\n".join(content_lines), title=t("Content & Temperature")))

    # Все LLM в таблице
    if data.available_llms:
        _print_rich_llms_table(console, data)
    else:
        console.print(_rich_imports.panel.fit(t("No LLMs added"), title=t("Available LLMs")))

    # Логирование
    logging_lines = []
    logging_lines.append(f"{t('Console log level')}: [bold]{data.console_log_level}[/bold]")
    
    if data.file_enabled:
        logging_lines.append(f"{t('File logging')}: [green]On[/green] ({data.file_log_level})")
    else:
        logging_lines.append(f"{t('File logging')}: [dim]Off[/dim]")
    
    console.print(_rich_imports.panel.fit("\n".join(logging_lines), title=t("Logging")))
    console.rule()


def _print_rich_llms_table(console, data: SettingsData) -> None:
    """Выводит таблицу LLM используя Rich."""
    table = _rich_imports.table(title=t("Available LLMs"), show_lines=False, expand=True)
    table.add_column(t("LLM"), style="bold")
    table.add_column(t("Model"))
    table.add_column("API URL")
    table.add_column(t("API key"))

    for name in data.available_llms:
        cfg = config.get_llm_config(name) or {}
        is_current = name == data.current_llm
        
        # Выделяем текущую LLM зеленым цветом
        if is_current:
            name_display = f"[green]{name}[/green]"
            model_display = f"[green]{cfg.get('model', '') or ''}[/green]"
            url_display = f"[green]{cfg.get('api_url', '') or ''}[/green]"
            key_display = f"[green]{format_api_key_display(cfg.get('api_key', '') or '')}[/green]"
        else:
            name_display = name
            model_display = cfg.get('model', '') or ''
            url_display = cfg.get('api_url', '') or ''
            key_display = format_api_key_display(cfg.get('api_key', '') or '')
        
        table.add_row(
            name_display,
            model_display,
            url_display,
            key_display,
        )
    
    console.print(table)


def print_settings_overview(console: Optional[object] = None) -> None:
    """
    Печатает обзор настроек. Использует Rich, если доступен, иначе обычный текст.

    Args:
        console: Опционально переданный rich.Console для вывода
    """
    try:
        if _rich_imports.available:
            _print_rich_overview(console)
        else:
            _plain_overview_print()
    
    except SettingsOverviewError:
        # Rich недоступен, используем обычный вывод
        _plain_overview_print()
    
    except Exception as e:
        print(f"⚠️ Ошибка при выводе настроек: {e}")
        _print_minimal_settings()


def get_settings_summary() -> Dict[str, Any]:
    """
    Возвращает краткую сводку настроек в виде словаря.
    
    Returns:
        Dict[str, Any]: Словарь с основными настройками
    """
    try:
        data = SettingsData()
        
        return {
            "current_llm": data.current_llm,
            "current_llm_configured": bool(data.current_config),
            "temperature": data.temperature,
            "user_content_length": len(data.user_content) if data.user_content != t("(empty)") else 0,
            "available_llms_count": len(data.available_llms),
            "console_log_level": data.console_log_level,
            "file_logging_enabled": data.file_enabled,
            "file_log_level": data.file_log_level if data.file_enabled else None
        }
    
    except Exception as e:
        return {
            "error": str(e),
            "available": False
        }


if __name__ == "__main__":
    # Тестирование функций модуля
    print("=== Тестирование settings_overview ===\n")
    
    print("1. Rich доступен:", _rich_imports.available)
    
    print("\n2. Сводка настроек:")
    summary = get_settings_summary()
    for key, value in summary.items():
        print(f"   {key}: {value}")
    
    print("\n3. Полный обзор настроек:")
    print_settings_overview()
    
    print("\n✅ Тестирование завершено!")
