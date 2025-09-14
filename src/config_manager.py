#!/usr/bin/env python3
"""
Модуль для управления конфигурацией приложения.
Использует JSON для всех настроек с современным меню навигацией стрелками.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, List, Optional
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.columns import Columns
from rich.align import Align
from rich.layout import Layout
from platformdirs import user_config_dir

try:
    from .formatter_text import _format_api_key_display
except ImportError:
    # Для случаев, когда модуль запускается напрямую
    from formatter_text import _format_api_key_display


# === Настройки ===
APP_NAME = "ai-ebash"
USER_CONFIG_DIR = Path(user_config_dir(APP_NAME))
USER_CONFIG_PATH = USER_CONFIG_DIR / "config.json"
DEFAULT_CONFIG_PATH = Path(__file__).parent / "default_config.json"


class MenuSystem:
    """Класс для создания интерактивного меню"""

    def __init__(self, console: Console):
        self.console = console

    def display_menu(self, title: str, options: List[str]) -> None:
        """Отображает меню с пронумерованными опциями"""
        self.console.clear()

        # Заголовок уже показан в run_configuration_menu
        self.console.print()

        # Опции меню
        for i, option in enumerate(options, 1):
            self.console.print(f"  [cyan]{i}[/cyan]. {option}")

        self.console.print()
        self.console.print("[dim]Введите номер пункта меню или 0 для выхода[/dim]")

    def navigate_menu(self, options: List[str], title: str) -> Optional[int]:
        """Простая навигация по меню с вводом номера"""
        while True:
            self.display_menu(title, options)

            try:
                choice = Prompt.ask("Ваш выбор", default="")
                if not choice:
                    continue

                choice_num = int(choice)
                if choice_num == 0:
                    return None
                elif 1 <= choice_num <= len(options):
                    return choice_num - 1
                else:
                    self.console.print(f"[red]Введите число от 1 до {len(options)} или 0 для выхода[/red]")
                    self.console.input("\n[cyan]Нажмите Enter для продолжения...[/cyan]")

            except ValueError:
                self.console.print("[red]Введите корректное число[/red]")
                self.console.input("\n[cyan]Нажмите Enter для продолжения...[/cyan]")
            except KeyboardInterrupt:
                return None

    def get_user_input(self, prompt: str, default: str = "", password: bool = False) -> str:
        """Получение ввода от пользователя"""
        if password:
            return Prompt.ask(prompt, default=default, password=True)
        return Prompt.ask(prompt, default=default)


class ConfigManager:
    """Класс для управления конфигурацией с современным меню"""

    def __init__(self):
        self.console = Console()
        self.menu = MenuSystem(self.console)
        self.json_config = {}
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

    def _show_current_settings(self) -> None:
        """Показывает текущие настройки перед главным меню"""
        current_context = self.get_value("global", "context", "")
        current_llm = self.get_current_llm_name()
        current_llm_config = self.get_current_llm_config()
        available_llms = self.get_available_llms()

        # Показываем контекст
        if current_context:
            context_panel = Panel(
                Text(current_context, style="white"),
                title="Контекст для всех нейронок",
                border_style="white",
                padding=(1, 2)
            )
            self.console.print(context_panel)
        else:
            context_panel = Panel(
                Text("[dim]Контекст не задан[/dim]", style="dim white"),
                title="[bold]Контекст[/bold]",
                border_style="white",
                padding=(1, 2)
            )
            self.console.print(context_panel)

        self.console.print()

        # Информация о текущей нейросети
        current_info = Table(show_header=False, box=None, padding=(0, 2))
        current_info.add_column("Параметр", style="white", no_wrap=True)
        current_info.add_column("Значение", style="white")

        current_info.add_row("Текущая нейросеть", current_llm)
        current_info.add_row("Модель", current_llm_config.get("model", "не указана"))
        current_info.add_row("API URL", current_llm_config.get("api_url", "не указан"))
        current_info.add_row("Всего нейросетей", str(len(available_llms)))

        info_panel = Panel(
            current_info,
            title="Текущая конфигурация",
            border_style="white",
            padding=(1, 2)
        )
        self.console.print(info_panel)

        self.console.print()

        # Показываем таблицу всех LLM
        self._show_llms_table()

    def get_available_llms(self) -> List[str]:
        """Возвращает список доступных LLM"""
        supported_llms = self.json_config.get("supported_LLMs", {})
        return list(supported_llms.keys())

    def run_configuration_menu(self) -> None:
        """Запускает главное меню конфигурации"""
        main_menu_options = [
            "Изменить контекст",
            "Выбрать нейросеть",
            "Добавить нейросеть",
            "Редактировать нейросеть",
            "Удалить нейросеть",
            "Language (в разработке)",
            "Выход"
        ]

        while True:
            # Показываем заголовок
            self.console.clear()
            title_panel = Panel(
                Align.center(Text("AI-ebash Конфигуратор", style="white")),
                border_style="white",
                padding=(1, 2)
            )
            self.console.print(title_panel)

            # Показываем текущие настройки
            self._show_current_settings()

            choice = self.menu.navigate_menu(main_menu_options, "AI-ebash Конфигуратор")

            if choice is None or choice == 6:  # Выход
                self._show_exit_message()
                break

            elif choice == 0:  # Изменить контекст
                self._set_context_menu()

            elif choice == 1:  # Выбрать нейросеть
                self._select_llm_menu()

            elif choice == 2:  # Добавить нейросеть
                self._add_llm_menu()

            elif choice == 3:  # Редактировать нейросеть
                self._edit_llm_menu()

            elif choice == 4:  # Удалить нейросеть
                self._delete_llm_menu()

            elif choice == 5:  # Language (заглушка)
                self._language_menu()

    def _set_context_menu(self) -> None:
        """Меню настройки контекста"""
        self.console.clear()

        current_context = self.get_value("global", "context", "")

        panel = Panel(
            Text("Текущий контекст:", style="white") + "\n\n" +
            (current_context if current_context else "[dim](не задан)[/dim]"),
            title="Настройка контекста",
            border_style="white"
        )
        self.console.print(panel)
        self.console.print()

        new_context = self.menu.get_user_input(
            "Введите новый контекст (или Enter для отмены)",
            default=current_context
        )

        if new_context and new_context != current_context:
            self.set_value("global", "context", new_context)
            self.console.print("[white]✓ Контекст обновлен![/white]")
        elif not new_context and current_context:
            if Confirm.ask("Очистить контекст?", default=False):
                self.set_value("global", "context", "")
                self.console.print("[white]✓ Контекст очищен![/white]")
        else:
            self.console.print("[dim]Контекст оставлен без изменений[/dim]")

        self.console.input("\n[cyan]Нажмите Enter для продолжения...[/cyan]")

    def _select_llm_menu(self) -> None:
        """Меню выбора нейросети"""
        available_llms = self.get_available_llms()
        current_llm = self.get_current_llm_name()

        if not available_llms:
            self.console.clear()
            self.console.print("[red]Нет доступных нейросетей![/red]")
            self.console.input("\n[cyan]Нажмите Enter для продолжения...[/cyan]")
            return

        # Создаем опции меню из доступных LLM
        menu_options = []
        for llm in available_llms:
            marker = " (текущая)" if llm == current_llm else ""
            menu_options.append(f"{llm}{marker}")

        choice = self.menu.navigate_menu(menu_options, "Выбор нейросети")

        if choice is not None:
            selected_llm = available_llms[choice]
            if selected_llm != current_llm:
                self.set_value("global", "current_LLM", selected_llm)
                self.console.clear()
                self.console.print(f"[white]✓ Выбрана нейросеть: {selected_llm}[/white]")
                # Показываем обновленную таблицу всех LLM
                self._show_llms_table()
            else:
                self.console.clear()
                self.console.print("[dim]Нейросеть оставлена без изменений[/dim]")

            # Показываем таблицу всех LLM


    def _show_all_llms_menu(self) -> None:
        """Меню показа всех нейросетей"""
        self.console.clear()

        panel = Panel(
            Text("Все доступные нейросети", style="white"),
            border_style="white"
        )
        self.console.print(panel)
        self.console.print()

        # Показываем таблицу всех LLM
        self._show_llms_table()

        self.console.input("\n[cyan]Нажмите Enter для продолжения...[/cyan]")

    def _show_llms_table(self) -> None:
        """Показывает таблицу всех LLM"""
        available_llms = self.get_available_llms()
        current_llm = self.get_current_llm_name()

        if not available_llms:
            return

        table = Table(title="Доступные нейросети", show_header=True, header_style="white")
        table.add_column("Название", style="white", no_wrap=True)
        table.add_column("Модель", style="dim white")
        table.add_column("API URL", style="dim white")
        table.add_column("API Key", style="dim white")
        table.add_column("Статус", style="cyan")

        for llm_name in available_llms:
            llm_config = self.json_config.get("supported_LLMs", {}).get(llm_name, {})
            model = llm_config.get("model", "не указана")
            api_url = llm_config.get("api_url", "не указан")
            api_key = _format_api_key_display(llm_config.get("api_key", ""))
            status = "✓ Текущая" if llm_name == current_llm else ""

            table.add_row(llm_name, model, api_url, api_key, status)

        self.console.print(table)
        self.console.print()

    def _delete_llm_menu(self) -> None:
        """Меню удаления нейросети"""
        self.console.clear()

        available_llms = self.get_available_llms()
        current_llm = self.get_current_llm_name()

        if not available_llms:
            self.console.print("[red]Нет нейросетей для удаления![/red]")
            self.console.input("\n[cyan]Нажмите Enter для продолжения...[/cyan]")
            return

        # Исключаем текущую нейросеть из списка для удаления
        deletable_llms = [llm for llm in available_llms if llm != current_llm]

        if not deletable_llms:
            self.console.print("[dim white]Нельзя удалить единственную нейросеть![/dim white]")
            self.console.input("\n[cyan]Нажмите Enter для продолжения...[/cyan]")
            return

        menu_options = [f"Удалить: {llm}" for llm in deletable_llms]

        choice = self.menu.navigate_menu(menu_options, "Удаление нейросети")

        if choice is not None:
            selected_llm = deletable_llms[choice]

            self.console.clear()
            if Confirm.ask(f"Удалить нейросеть '{selected_llm}'?", default=False):
                del self.json_config["supported_LLMs"][selected_llm]
                self._save_json_config()
                self.console.print(f"[white]✓ Нейросеть '{selected_llm}' удалена![/white]")
                # Показываем обновленную таблицу всех LLM
                self._show_llms_table()
            else:
                self.console.print("[dim]Удаление отменено[/dim]")

    def _add_llm_menu(self) -> None:
        """Меню добавления новой нейросети"""
        self.console.clear()

        panel = Panel(
            Text("Добавление новой нейросети", style="white"),
            border_style="white"
        )
        self.console.print(panel)
        self.console.print()

        # Ввод данных
        name = self.menu.get_user_input("Название нейросети")
        if not name:
            self.console.print("[red]Название не может быть пустым![/red]")
            self.console.input("\n[cyan]Нажмите Enter для продолжения...[/cyan]")
            return

        # Проверяем, существует ли уже такая нейросеть
        if name in self.get_available_llms():
            self.console.print(f"[red]Нейросеть '{name}' уже существует![/red]")
            self.console.input("\n[cyan]Нажмите Enter для продолжения...[/cyan]")
            return

        model = self.menu.get_user_input("Модель")
        api_url = self.menu.get_user_input("API URL")
        api_key = self.menu.get_user_input("API Key", password=True)

        # Создаем конфигурацию
        new_llm_config = {
            "model": model,
            "api_url": api_url,
            "api_key": api_key
        }

        # Сохраняем
        self.json_config.setdefault("supported_LLMs", {})[name] = new_llm_config
        self._save_json_config()

        self.console.print(f"[white]✓ Нейросеть '{name}' добавлена![/white]")
        
        # Показываем таблицу всех LLM
        self._show_llms_table()

    def _edit_llm_menu(self) -> None:
        """Меню редактирования нейросети"""
        available_llms = self.get_available_llms()

        if not available_llms:
            self.console.clear()
            self.console.print("[red]Нет нейросетей для редактирования![/red]")
            self.console.input("\n[cyan]Нажмите Enter для продолжения...[/cyan]")
            return

        menu_options = [f"Редактировать: {llm}" for llm in available_llms]

        choice = self.menu.navigate_menu(menu_options, "Редактирование нейросети")

        if choice is not None:
            selected_llm = available_llms[choice]
            self._edit_specific_llm(selected_llm)
        


    def _edit_specific_llm(self, llm_name: str) -> None:
        """Редактирование конкретной нейросети"""
        self.console.clear()

        current_config = self.json_config.get("supported_LLMs", {}).get(llm_name, {})

        panel = Panel(
            Text(f"Редактирование нейросети: {llm_name}", style="white"),
            border_style="white"
        )
        self.console.print(panel)
        self.console.print()

        # Показываем текущие значения
        self.console.print(f"Текущее название: [white]{llm_name}[/white]")
        self.console.print(f"Текущая модель: [dim white]{current_config.get('model', 'не указана')}[/dim white]")
        self.console.print(f"Текущий API URL: [dim white]{current_config.get('api_url', 'не указан')}[/dim white]")
        self.console.print(f"API Key: [dim white]{_format_api_key_display(current_config.get('api_key', ''))}[/dim white]")
        self.console.print()

        # Ввод нового названия
        new_name = self.menu.get_user_input(
            "Новое название нейросети",
            default=llm_name
        )

        # Проверяем новое название
        if new_name != llm_name:
            if not new_name:
                self.console.print("[red]Название не может быть пустым![/red]")
                self.console.input("\n[cyan]Нажмите Enter для продолжения...[/cyan]")
                return

            if new_name in self.get_available_llms():
                self.console.print(f"[red]Нейросеть '{new_name}' уже существует![/red]")
                self.console.input("\n[cyan]Нажмите Enter для продолжения...[/cyan]")
                return

        # Ввод новых значений
        new_model = self.menu.get_user_input(
            "Модель",
            default=current_config.get('model', '')
        )
        new_api_url = self.menu.get_user_input(
            "API URL",
            default=current_config.get('api_url', '')
        )
        new_api_key = self.menu.get_user_input(
            "API Key (оставьте пустым, чтобы не менять)",
            password=True
        )

        # Обновляем конфигурацию
        updated_config = current_config.copy()
        if new_model:
            updated_config['model'] = new_model
        if new_api_url:
            updated_config['api_url'] = new_api_url
        if new_api_key:  # Только если ввели новый ключ
            updated_config['api_key'] = new_api_key

        # Сохраняем изменения
        if new_name != llm_name:
            # Удаляем старую конфигурацию
            del self.json_config["supported_LLMs"][llm_name]
            # Сохраняем под новым именем
            self.json_config.setdefault("supported_LLMs", {})[new_name] = updated_config

            # Если это была текущая нейросеть, обновляем ссылку
            if self.get_current_llm_name() == llm_name:
                self.set_value("global", "current_LLM", new_name)

            self.console.print(f"[white]✓ Нейросеть переименована в '{new_name}' и обновлена![/white]")
        else:
            # Просто обновляем существующую
            self.json_config.setdefault("supported_LLMs", {})[llm_name] = updated_config
            self.console.print(f"[white]✓ Нейросеть '{llm_name}' обновлена![/white]")

        self._save_json_config()

        # Показываем таблицу всех LLM
        self._show_llms_table()

    def _language_menu(self) -> None:
        """Заглушка для меню языка"""
        self.console.clear()

        panel = Panel(
            Text("Функция выбора языка находится в разработке", style="white"),
            title="Language",
            border_style="white"
        )
        self.console.print(panel)
        self.console.input("\n[cyan]Нажмите Enter для продолжения...[/cyan]")

    def _show_exit_message(self) -> None:
        """Показывает сообщение при выходе"""
        self.console.clear()

        panel = Panel(
            Text("Спасибо за использование AI-ebash!", style="white"),
            border_style="white"
        )
        self.console.print(panel)


# Создаем глобальный экземпляр
config_manager = ConfigManager()


def run_configuration_dialog() -> None:
    """Запуск интерактивной настройки"""
    config_manager.run_configuration_menu()


if __name__ == "__main__":
    run_configuration_dialog()
