#!/usr/bin/env python3
"""
Модуль для управления конфигурацией приложения.
Использует JSON для всех настроек.
"""

import json
from pathlib import Path
from typing import Dict, Any, List
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from platformdirs import user_config_dir


# === Настройки ===
APP_NAME = "ai-ebash"
USER_CONFIG_DIR = Path(user_config_dir(APP_NAME))
USER_CONFIG_PATH = USER_CONFIG_DIR / "config.json"
DEFAULT_CONFIG_PATH = Path(__file__).parent / "default_config.json"


def _format_api_key_display(api_key: str) -> str:
    """Форматирует отображение API ключа для таблиц"""
    if not api_key:
        return "(не задан)"
    elif len(api_key) <= 10:
        return api_key
    else:
        return f"{api_key[:5]}...{api_key[-5:]}"


class ConfigManager:
    """Класс для управления конфигурацией с интерактивной настройкой"""

    def __init__(self):
        self.console = Console()
        self.json_config = {}  # Для хранения полной JSON структуры
        self._ensure_config_exists()
        self._load_json_config()

    def _ensure_config_exists(self) -> None:
        """Убеждается, что файл конфигурации существует"""
        try:
            if not USER_CONFIG_PATH.exists():
                USER_CONFIG_DIR.mkdir(parents=True, exist_ok=True)
                if DEFAULT_CONFIG_PATH.exists():
                    import shutil
                    shutil.copy(DEFAULT_CONFIG_PATH, USER_CONFIG_PATH)
        except Exception as e:
            self.console.print(f"[red]Ошибка при создании файла конфигурации: {e}[/red]")

    def _load_json_config(self) -> None:
        """Загружает полную конфигурацию из JSON"""
        try:
            with open(USER_CONFIG_PATH, 'r', encoding='utf-8') as f:
                self.json_config = json.load(f)
        except Exception:
            self.json_config = {}

    def _save_json_config(self) -> None:
        """Сохраняет полную конфигурацию в JSON"""
        try:
            USER_CONFIG_DIR.mkdir(parents=True, exist_ok=True)
            with open(USER_CONFIG_PATH, 'w', encoding='utf-8') as f:
                json.dump(self.json_config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.console.print(f"[red]Ошибка сохранения настроек: {e}[/red]")

    def get_value(self, section: str, key: str, default: Any = None) -> Any:
        """Получает значение из настроек"""
        return self.json_config.get(section, {}).get(key, default)

    def set_value(self, section: str, key: str, value: Any) -> None:
        """Устанавливает значение в настройках"""
        self.json_config.setdefault(section, {})[key] = value
        self._save_json_config()

    def get_logging_config(self) -> Dict[str, Any]:
        """Возвращает настройки логирования"""
        return self.json_config.get("logging", {})

    def get_current_llm_name(self) -> str:
        """Возвращает имя текущего LLM"""
        return self.json_config.get("global", {}).get("current_LLM", "openai_over_proxy")

    def get_current_llm_config(self) -> Dict[str, Any]:
        """Возвращает конфигурацию текущего LLM"""
        current_llm = self.get_current_llm_name()
        return self.json_config.get("supported_LLMs", {}).get(current_llm, {})

    def get_available_llms(self) -> List[str]:
        """Возвращает список доступных LLM"""
        supported_llms = self.json_config.get("supported_LLMs", {})
        return list(supported_llms.keys())

    def run_interactive_setup(self) -> None:
        """Запускает интерактивную настройку"""

        # Настройка global параметров
        self._configure_global_settings()

        # Выбор текущего LLM
        self._configure_current_llm()

        # Управление LLM
        if Confirm.ask("Хотите управлять списком LLM?", default=False):
            self._manage_llms()

        # Сохранение
        self._save_json_config()
        self.console.print("\n[green]✅ Настройки сохранены![/green]")

        # Напоминание о безопасности
        self._show_security_reminder()

    def _configure_global_settings(self) -> None:
        """Настройка глобальных параметров"""
        self.console.print(Panel(Text("Здесь и далее, чтобы оставить текущее значение - нажмите Enter. Прервать настройку - Ctrl+C", justify="center"), title="Настройка AI-ebash!", expand=False))

        # Список параметров для настройки
        global_settings = [
            ("context", "Системный контекст для ИИ:", self.get_value("global", "context", "")),
        ]

        for key, description, current_value in global_settings:
            self._configure_single_setting(key, description, current_value)

    def _configure_single_setting(self, key: str, description: str, current_value: str) -> None:
        """Настройка одного параметра"""
        new_value = Prompt.ask(description, default=current_value or "")

        if new_value != current_value:
            self.set_value("global", key, new_value)
            self.console.print(f"[green]✓ Обновлено[/green]")
        else:
            self.console.print("[dim]Оставлено без изменений[/dim]")

        self.console.print()

    def _configure_current_llm(self) -> None:
        """Выбор текущего LLM"""
        self.console.print("[bold]Выбор нейросети для общения:[/bold]\n")

        available_llms = self.get_available_llms()
        current_llm = self.get_current_llm_name()

        if not available_llms:
            self.console.print("[red]Нет доступных LLM![/red]")
            return

        # Показываем таблицу LLM
        table = Table(title="Доступные нейросети")
        table.add_column("№", style="cyan", no_wrap=True)
        table.add_column("LLM", style="magenta")
        table.add_column("Модель", style="green")
        table.add_column("API Key", style="red")
        table.add_column("Текущий", style="yellow")

        for i, llm_name in enumerate(available_llms, 1):
            llm_config = self.json_config.get("supported_LLMs", {}).get(llm_name, {})
            model = llm_config.get("model", "не указана")
            api_key = _format_api_key_display(llm_config.get("api_key", ""))
            is_current = "✓" if llm_name == current_llm else ""

            table.add_row(str(i), llm_name, model, api_key, is_current)

        self.console.print(table)
        self.console.print()

        # Выбор
        try:
            default_choice = str(available_llms.index(current_llm) + 1) if current_llm in available_llms else "1"
            choice = Prompt.ask(
                f"Выберите LLM (1-{len(available_llms)})",
                default=default_choice
            )

            choice_num = int(choice)
            if 1 <= choice_num <= len(available_llms):
                selected_llm = available_llms[choice_num - 1]
                if selected_llm != current_llm:
                    self.set_value("global", "current_LLM", selected_llm)
                    self.console.print(f"[green]✓ Выбран LLM: {selected_llm}[/green]")
                else:
                    self.console.print("[dim]LLM оставлен без изменений[/dim]")
            else:
                self.console.print(f"[red]Введите число от 1 до {len(available_llms)}[/red]")

        except ValueError:
            self.console.print("[red]Введите корректное число[/red]")
        except KeyboardInterrupt:
            self.console.print(f"\n[dim]LLM оставлен без изменений: {current_llm}[/dim]")

    def _manage_llms(self) -> None:
        """Управление списком LLM"""
        actions = {
            "1": ("Настроить LLM", self._configure_llm),
            "2": ("Удалить LLM", self._remove_llm),
            "3": ("Просмотреть все LLM", self._show_llms),
            "4": ("Вернуться к настройкам", None)
        }

        while True:
            self.console.print("\n[bold]Управление LLM:[/bold]")
            for key, (description, _) in actions.items():
                self.console.print(f"{key}. {description}")

            choice = Prompt.ask("Выберите действие", choices=list(actions.keys()))

            if choice == "4":
                break

            action_name, action_func = actions[choice]
            if action_func:
                action_func()

    def _configure_llm(self) -> None:
        """Настройка существующего LLM через интерфейс"""
        available_llms = self.get_available_llms()

        if not available_llms:
            self.console.print("[yellow]Нет доступных LLM для настройки![/yellow]")
            return

        self.console.print("\n[bold]Выберите LLM для настройки:[/bold]")

        for i, llm_name in enumerate(available_llms, 1):
            llm_config = self.json_config.get("supported_LLMs", {}).get(llm_name, {})
            model = llm_config.get("model", "не указана")
            self.console.print(f"{i}. {llm_name} (модель: {model})")

        while True:
            try:
                choice = Prompt.ask(f"Выберите LLM для настройки (1-{len(available_llms)})")
                choice_num = int(choice)

                if 1 <= choice_num <= len(available_llms):
                    selected_llm = available_llms[choice_num - 1]
                    self._configure_specific_llm(selected_llm)
                    break
                else:
                    self.console.print(f"[red]Введите число от 1 до {len(available_llms)}[/red]")

            except ValueError:
                self.console.print("[red]Введите корректное число[/red]")

    def _configure_specific_llm(self, llm_name: str) -> None:
        """Настройка конкретного LLM через его интерфейс"""
        try:
            llm_config = self.json_config.get("supported_LLMs", {}).get(llm_name, {})
            model = llm_config.get("model", "")
            api_url = llm_config.get("api_url", "")
            api_key = llm_config.get("api_key", "")

            from aiebash.llm_factory import create_llm_client
            client = create_llm_client(
                backend=llm_name,
                model=model,
                api_url=api_url,
                api_key=api_key
            )

            updated_config = client.configure_llm(self.console)
            self.json_config.setdefault("supported_LLMs", {})[llm_name] = updated_config

            self.console.print(f"[green]Настройки для '{llm_name}' обновлены[/green]")

        except Exception as e:
            self.console.print(f"[red]Ошибка при настройке LLM '{llm_name}': {e}[/red]")

    def _remove_llm(self) -> None:
        """Удаление LLM"""
        available_llms = self.get_available_llms()
        current_llm = self.get_current_llm_name()

        if not available_llms:
            self.console.print("[red]Нет LLM для удаления[/red]")
            return

        self.console.print("\n[bold]Удаление LLM:[/bold]")

        for i, llm in enumerate(available_llms, 1):
            marker = " (текущий)" if llm == current_llm else ""
            self.console.print(f"{i}. {llm}{marker}")

        while True:
            try:
                choice = Prompt.ask(f"Выберите LLM для удаления (1-{len(available_llms)})")
                choice_num = int(choice)

                if 1 <= choice_num <= len(available_llms):
                    selected_llm = available_llms[choice_num - 1]

                    if selected_llm == current_llm:
                        self.console.print("[red]Нельзя удалить текущий LLM[/red]")
                        return

                    if Confirm.ask(f"Удалить LLM '{selected_llm}'?", default=False):
                        del self.json_config["supported_LLMs"][selected_llm]
                        self.console.print(f"[green]✓ LLM '{selected_llm}' удален[/green]")
                    break
                else:
                    self.console.print(f"[red]Введите число от 1 до {len(available_llms)}[/red]")

            except ValueError:
                self.console.print("[red]Введите корректное число[/red]")

    def _show_llms(self) -> None:
        """Показать все LLM"""
        available_llms = self.get_available_llms()
        current_llm = self.get_current_llm_name()

        if not available_llms:
            self.console.print("[red]Нет доступных LLM[/red]")
            return

        table = Table(title="Все LLM")
        table.add_column("LLM", style="magenta")
        table.add_column("Модель", style="green")
        table.add_column("API URL", style="blue")
        table.add_column("API Key", style="red")
        table.add_column("Статус", style="yellow")

        for llm_name in available_llms:
            llm_config = self.json_config.get("supported_LLMs", {}).get(llm_name, {})
            model = llm_config.get("model", "не указана")
            api_url = llm_config.get("api_url", "не указан")
            api_key = _format_api_key_display(llm_config.get("api_key", ""))
            status = "Текущий" if llm_name == current_llm else ""

            table.add_row(llm_name, model, api_url, api_key, status)

        self.console.print(table)

    def _show_security_reminder(self) -> None:
        """Показать напоминание о безопасности"""
        panel = Panel(
            Text.from_markup(
                "[bold red]🔒 ВАЖНО![/bold red]\n\n"
                "API ключи хранятся в открытом виде в config.json\n"
                "Рекомендуется:\n"
                "• Использовать переменные окружения\n"
                "• Установить права доступа только для владельца\n"
                "• Не коммитить ключи в git\n\n"
                "[cyan]Пример:[/cyan]\n"
                "export AIEBASH_OPENAI_API_KEY=your_key_here"
            ),
            title="Безопасность",
            border_style="red"
        )
        self.console.print(panel)


# Создаем глобальный экземпляр
config_manager = ConfigManager()


def run_configuration_dialog() -> None:
    """Запуск интерактивной настройки"""
    config_manager.run_interactive_setup()


if __name__ == "__main__":
    run_configuration_dialog()
