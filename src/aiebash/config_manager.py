#!/usr/bin/env python3
"""
Новый менеджер конфигурации для приложения ai-ebash.

ОСОБЕННОСТИ:
- Автоматическое создание config.yaml из default_config.yaml при первом запуске
- Удобные свойства для доступа к основным настройкам
- Полная поддержка YAML формата
- Безопасная работа с файлами конфигурации

ПРИМЕРЫ ИСПОЛЬЗОВАНИЯ:

# Базовое использование
from config_manager import config

# Чтение настроек
current_llm = config.current_llm
temperature = config.temperature
user_content = config.user_content

# Изменение настроек
config.temperature = 0.7
config.stream_mode = True
config.user_content = "Новый контент"

# Работа с LLM
available_llms = config.get_available_llms()
current_config = config.get_current_llm_config()

# Добавление новой LLM
config.add_llm("My LLM", "gpt-4", "https://api.example.com/v1", "api-key")

# Сброс к настройкам по умолчанию
config.reset_to_defaults()
"""

import yaml
import os
import shutil
from pathlib import Path
from typing import Dict, Any, Optional, List
from platformdirs import user_config_dir
from aiebash.i18n import detect_system_language


class ConfigError(Exception):
    """Исключение для ошибок конфигурации."""
    pass


class ConfigSections:
    """Константы для разделов конфигурации."""
    GLOBAL = "global"
    LOGGING = "logging"
    SUPPORTED_LLMS = "supported_LLMs"


class GlobalKeys:
    """Константы для ключей глобального раздела."""
    CURRENT_LLM = "current_LLM"
    USER_CONTENT = "user_content"
    TEMPERATURE = "temperature"
    STREAM_OUTPUT_MODE = "stream_output_mode"
    JSON_MODE = "json_mode"


class LoggingKeys:
    """Константы для ключей раздела логирования."""
    CONSOLE_LEVEL = "console_level"
    FILE_ENABLED = "file_enabled"
    FILE_LEVEL = "file_level"


class ConfigManager:
    """
    Менеджер конфигурации для управления настройками приложения.

    Автоматически создает файл конфигурации из шаблона default_config.yaml,
    если пользовательский config.yaml не существует.
    """

    def __init__(self, app_name: str = "ai-ebash"):
        """
        Инициализация менеджера конфигурации.

        Args:
            app_name: Имя приложения для определения директории конфигурации
        """
        self.app_name = app_name
        self.user_config_dir = Path(user_config_dir(app_name))
        self.user_config_path = self.user_config_dir / "config.yaml"
        self._default_config_path = Path(__file__).parent / "default_config.yaml"

        # Создаем директорию если не существует
        self.user_config_dir.mkdir(parents=True, exist_ok=True)

        # Автоматически создаем конфигурацию из шаблона если нужно
        self._ensure_config_exists()

        # Загружаем конфигурацию
        self._config = self._load_config()

    def _ensure_config_exists(self) -> None:
        """
        Убеждается, что файл конфигурации существует.
        Если config.yaml не найден, копирует default_config.yaml.
        """
        if not self.user_config_path.exists():
            if self._default_config_path.exists():
                try:
                    shutil.copy2(self._default_config_path, self.user_config_path)
                    # After creating user config from defaults, set language based on system locale
                    try:
                        with open(self.user_config_path, 'r', encoding='utf-8') as f:
                            cfg = yaml.safe_load(f) or {}
                        sys_lang = detect_system_language(["en", "ru"]) or "en"
                        cfg["language"] = sys_lang
                        with open(self.user_config_path, 'w', encoding='utf-8') as f:
                            yaml.safe_dump(cfg, f, indent=2, allow_unicode=True, default_flow_style=False, sort_keys=False)
                    except Exception:
                        pass
                    print(f"Создана конфигурация из шаблона: {self.user_config_path}")
                except Exception as e:
                    raise RuntimeError(f"Не удалось создать файл конфигурации: {e}")
            else:
                raise FileNotFoundError(f"Файл шаблона конфигурации не найден: {self._default_config_path}")

    def _load_config(self) -> Dict[str, Any]:
        """
        Загружает конфигурацию из YAML файла.

        Returns:
            Dict[str, Any]: Загруженная конфигурация
        
        Raises:
            ConfigError: При критических ошибках загрузки
        """
        try:
            with open(self.user_config_path, 'r', encoding='utf-8') as f:
                config_data = yaml.safe_load(f)
                if config_data is None:
                    return {}
                if not isinstance(config_data, dict):
                    raise ConfigError(f"Неверный формат конфигурации: ожидался словарь, получен {type(config_data)}")
                return config_data
        except FileNotFoundError:
            print(f"⚠️  Файл конфигурации не найден: {self.user_config_path}")
            return {}
        except yaml.YAMLError as e:
            raise ConfigError(f"Ошибка парсинга YAML: {e}")
        except Exception as e:
            print(f"⚠️  Ошибка загрузки конфигурации: {e}")
            return {}

    def _save_config(self) -> None:
        """
        Сохраняет текущую конфигурацию в YAML файл с созданием резервной копии.
        
        Raises:
            ConfigError: При ошибке сохранения
        """
        # Создаем резервную копию перед сохранением
        backup_path = self.user_config_path.with_suffix('.yaml.backup')
        if self.user_config_path.exists():
            try:
                shutil.copy2(self.user_config_path, backup_path)
            except Exception as e:
                print(f"⚠️  Не удалось создать резервную копию: {e}")
        
        try:
            # Проверяем валидность данных перед сохранением
            if not isinstance(self._config, dict):
                raise ConfigError("Конфигурация должна быть словарем")
            
            with open(self.user_config_path, 'w', encoding='utf-8') as f:
                yaml.safe_dump(
                    self._config,
                    f,
                    indent=2,
                    allow_unicode=True,
                    default_flow_style=False,
                    sort_keys=False
                )
        except Exception as e:
            # Восстанавливаем из резервной копии при ошибке
            if backup_path.exists():
                try:
                    shutil.copy2(backup_path, self.user_config_path)
                    print(f"🔄 Конфигурация восстановлена из резервной копии")
                except Exception:
                    pass
            raise ConfigError(f"Не удалось сохранить конфигурацию: {e}")

    def reload(self) -> None:
        """
        Перезагружает конфигурацию из файла.
        """
        self._config = self._load_config()

    def save(self) -> None:
        """
        Сохраняет текущую конфигурацию в файл.
        """
        self._save_config()

    def get(self, section: str, key: str = None, default: Any = None) -> Any:
        """
        Получает значение из конфигурации.

        Args:
            section: Секция конфигурации (например, 'global', 'logging')
            key: Ключ в секции (если None, возвращает всю секцию)
            default: Значение по умолчанию

        Returns:
            Значение из конфигурации или default
        """
        section_data = self._config.get(section, {})

        if key is None:
            return section_data

        return section_data.get(key, default)

    def set(self, section: str, key: str, value: Any) -> None:
        """
        Устанавливает значение в конфигурации с валидацией.

        Args:
            section: Секция конфигурации
            key: Ключ в секции
            value: Новое значение
        
        Raises:
            ConfigError: При неверных параметрах
        """
        if not isinstance(section, str) or not section.strip():
            raise ConfigError("Секция должна быть непустой строкой")
        if not isinstance(key, str) or not key.strip():
            raise ConfigError("Ключ должен быть непустой строкой")
        
        if section not in self._config:
            self._config[section] = {}
        
        # Валидация для специфических ключей
        if section == ConfigSections.GLOBAL and key == GlobalKeys.TEMPERATURE:
            if not isinstance(value, (int, float)) or not (0 <= value <= 2):
                raise ConfigError("Температура должна быть числом от 0 до 2")
        
        self._config[section][key] = value
        self._save_config()

    def update_section(self, section: str, data: Dict[str, Any]) -> None:
        """
        Обновляет всю секцию конфигурации.

        Args:
            section: Секция для обновления
            data: Новые данные секции
        """
        self._config[section] = data
        self._save_config()

    def get_all(self) -> Dict[str, Any]:
        """
        Возвращает всю конфигурацию.

        Returns:
            Dict[str, Any]: Полная конфигурация
        """
        return self._config.copy()

    # === Удобные методы для работы с конкретными настройками ===

    @property
    def current_llm(self) -> str:
        """Текущая выбранная LLM."""
        return self.get("global", "current_LLM", "")

    @current_llm.setter
    def current_llm(self, value: str) -> None:
        """Устанавливает текущую LLM."""
        self.set("global", "current_LLM", value)

    @property
    def user_content(self) -> str:
        """Пользовательский контент для всех LLM."""
        return self.get("global", "user_content", "")

    @user_content.setter
    def user_content(self, value: str) -> None:
        """Устанавливает пользовательский контент."""
        self.set("global", "user_content", value)

    @property
    def temperature(self) -> float:
        """Температура генерации ответов."""
        return self.get("global", "temperature", 0.2)

    @temperature.setter
    def temperature(self, value: float) -> None:
        """Устанавливает температуру генерации."""
        self.set("global", "temperature", value)

    @property
    def stream_mode(self) -> bool:
        """Режим потокового вывода."""
        return self.get("global", "stream_output_mode", False)

    @stream_mode.setter
    def stream_mode(self, value: bool) -> None:
        """Устанавливает режим потокового вывода."""
        self.set("global", "stream_output_mode", value)

    @property
    def json_mode(self) -> bool:
        """JSON режим."""
        return self.get("global", "json_mode", False)

    @json_mode.setter
    def json_mode(self, value: bool) -> None:
        """Устанавливает JSON режим."""
        self.set("global", "json_mode", value)

    @property
    def console_log_level(self) -> str:
        """Уровень логирования в консоль."""
        return self.get("logging", "console_level", "CRITICAL")

    @console_log_level.setter
    def console_log_level(self, value: str) -> None:
        """Устанавливает уровень логирования в консоль."""
        self.set("logging", "console_level", value)

    @property
    def file_enabled(self) -> bool:
        """Включение логирования в файл."""
        return self.get("logging", "file_enabled", False)

    @file_enabled.setter
    def file_enabled(self, value: bool) -> None:
        """Устанавливает включение логирования в файл."""
        self.set("logging", "file_enabled", value)

    @property
    def file_log_level(self) -> str:
        """Уровень логирования в файл."""
        return self.get("logging", "file_level", "DEBUG")

    @file_log_level.setter
    def file_log_level(self, value: str) -> None:
        """Устанавливает уровень логирования в файл."""
        self.set("logging", "file_level", value)

    def get_available_llms(self) -> List[str]:
        """
        Возвращает список доступных LLM.

        Returns:
            List[str]: Список имен LLM
        """
        supported_llms = self.get("supported_LLMs")
        if isinstance(supported_llms, dict):
            return list(supported_llms.keys())
        return []

    def get_llm_config(self, llm_name: str) -> Dict[str, Any]:
        """
        Возвращает конфигурацию конкретной LLM.

        Args:
            llm_name: Имя LLM

        Returns:
            Dict[str, Any]: Конфигурация LLM
        """
        supported_llms = self.get("supported_LLMs")
        if isinstance(supported_llms, dict):
            return supported_llms.get(llm_name, {})
        return {}

    def get_current_llm_config(self) -> Dict[str, Any]:
        """
        Возвращает конфигурацию текущей LLM.

        Returns:
            Dict[str, Any]: Конфигурация текущей LLM
        """
        return self.get_llm_config(self.current_llm)

    def add_llm(self, name: str, model: str, api_url: str, api_key: str = "") -> None:
        """
        Добавляет новую LLM.

        Args:
            name: Имя LLM
            model: Модель LLM
            api_url: API URL
            api_key: API ключ (опционально)
        """
        supported_llms = self.get("supported_LLMs") or {}

        if name in supported_llms:
            raise ValueError(f"LLM с именем '{name}' уже существует")

        supported_llms[name] = {
            "model": model,
            "api_url": api_url,
            "api_key": api_key
        }

        self.set("supported_LLMs", name, supported_llms[name])

    def update_llm(self, name: str, model: str = None, api_url: str = None, api_key: str = None) -> None:
        """
        Обновляет конфигурацию LLM.

        Args:
            name: Имя LLM для обновления
            model: Новая модель (опционально)
            api_url: Новый API URL (опционально)
            api_key: Новый API ключ (опционально)
        """
        supported_llms = self.get("supported_LLMs") or {}

        if name not in supported_llms:
            raise ValueError(f"LLM с именем '{name}' не найдена")

        # Создаем копию текущей конфигурации
        current_config = supported_llms[name].copy()

        if model is not None:
            current_config["model"] = model
        if api_url is not None:
            current_config["api_url"] = api_url
        if api_key is not None:
            current_config["api_key"] = api_key

        # Обновляем всю секцию supported_LLMs
        supported_llms[name] = current_config
        self.update_section("supported_LLMs", supported_llms)

    def remove_llm(self, name: str) -> None:
        """
        Удаляет LLM.

        Args:
            name: Имя LLM для удаления
        """
        if name == self.current_llm:
            raise ValueError("Нельзя удалить текущую LLM")

        supported_llms = self.get("supported_LLMs") or {}

        if name not in supported_llms:
            raise ValueError(f"LLM с именем '{name}' не найдена")

        del supported_llms[name]
        self.update_section("supported_LLMs", supported_llms)

    def reset_to_defaults(self) -> None:
        """
        Сбрасывает конфигурацию к настройкам по умолчанию.
        """
        if self._default_config_path.exists():
            shutil.copy2(self._default_config_path, self.user_config_path)
            self.reload()
        else:
            raise FileNotFoundError("Файл с настройками по умолчанию не найден")

    @property
    def config_path(self) -> Path:
        """Путь к файлу конфигурации."""
        return self.user_config_path

    @property
    def default_config_path(self) -> Path:
        """Путь к файлу с настройками по умолчанию."""
        return self._default_config_path

    def validate_config(self) -> List[str]:
        """
        Проверяет конфигурацию на корректность.
        
        Returns:
            List[str]: Список найденных проблем (пустой если все ОК)
        """
        issues = []
        
        # Проверяем температуру
        temp = self.get(ConfigSections.GLOBAL, GlobalKeys.TEMPERATURE, 0.2)
        if not isinstance(temp, (int, float)) or not (0 <= temp <= 2):
            issues.append(f"Некорректная температура: {temp}")
        
        # Проверяем текущую LLM
        current_llm = self.get(ConfigSections.GLOBAL, GlobalKeys.CURRENT_LLM)
        if current_llm:
            available_llms = self.get_available_llms()
            if current_llm not in available_llms:
                issues.append(f"Текущая LLM '{current_llm}' не найдена в доступных")
        
        return issues
    
    def get_config_info(self) -> Dict[str, Any]:
        """
        Возвращает информацию о конфигурации.
        
        Returns:
            Dict[str, Any]: Информация о конфигурации
        """
        return {
            "config_path": str(self.user_config_path),
            "default_config_path": str(self._default_config_path),
            "config_exists": self.user_config_path.exists(),
            "default_exists": self._default_config_path.exists(),
            "config_size": self.user_config_path.stat().st_size if self.user_config_path.exists() else 0,
            "available_llms": len(self.get_available_llms()),
            "current_llm": self.current_llm,
            "validation_issues": self.validate_config()
        }
    
    def backup_config(self, backup_name: Optional[str] = None) -> Path:
        """
        Создает именованную резервную копию конфигурации.
        
        Args:
            backup_name: Имя для резервной копии (по умолчанию с timestamp)
        
        Returns:
            Path: Путь к созданной резервной копии
        """
        if backup_name is None:
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"config_backup_{timestamp}.yaml"
        
        backup_path = self.user_config_dir / backup_name
        
        if self.user_config_path.exists():
            shutil.copy2(self.user_config_path, backup_path)
        else:
            raise ConfigError("Файл конфигурации не существует")
        
        return backup_path
    
    def __repr__(self) -> str:
        return f"ConfigManager(app_name='{self.app_name}', config_path='{self.user_config_path}')"

    # === Language ===
    @property
    def language(self) -> str:
        """Current UI language (top-level key)."""
        try:
            return self._config.get("language", "en")
        except Exception:
            return "en"

    @language.setter
    def language(self, value: str) -> None:
        try:
            self._config["language"] = value
            self._save_config()
        except Exception:
            pass


# Глобальный экземпляр для удобства использования
config = ConfigManager()


if __name__ == "__main__":
    # Пример использования
    print("=== Тестирование ConfigManager ===")

    # Показываем текущие настройки
    print(f"Текущая LLM: {config.current_llm}")
    print(f"Температура: {config.temperature}")
    print(f"Потоковый режим: {config.stream_mode}")
    print(f"JSON режим: {config.json_mode}")
    print(f"Уровень логирования: {config.console_log_level}")
    print(f"Доступные LLM: {config.get_available_llms()}")

    # Показываем конфигурацию текущей LLM
    current_llm_config = config.get_current_llm_config()
    print(f"Конфигурация текущей LLM: {current_llm_config}")

    print("\n✅ ConfigManager работает корректно!")
