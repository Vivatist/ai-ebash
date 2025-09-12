from pathlib import Path
import yaml
import os
import shutil
import configparser
from typing import Dict, Any, Optional
from platformdirs import user_config_dir

# --- Пути к конфигурации ---
APP_NAME = "ai-ebash"
# Путь к конфигу пользователя (e.g., %APPDATA%\ai-ebash\config.yaml)
USER_CONFIG_DIR = Path(user_config_dir(APP_NAME))
USER_CONFIG_PATH = USER_CONFIG_DIR / "config.yaml"
# Путь к дефолтному конфигу
DEFAULT_CONFIG_PATH = Path(__file__).parent / "default_config.yaml"

class Settings:
    """Класс для работы с настройками приложения"""
    def __init__(self):
        self.config_data = {}
        self.load_settings()
        
    def load_settings(self) -> None:
        """Загружает настройки из файла или создает файл с настройками по умолчанию"""
        
        # Если файл настроек пользователя не существует
        if not USER_CONFIG_PATH.exists():
            # Создаем директорию, если ее нет
            USER_CONFIG_DIR.mkdir(parents=True, exist_ok=True)
            # Копируем дефолтный конфиг
            shutil.copy(DEFAULT_CONFIG_PATH, USER_CONFIG_PATH)
        
        # Загружаем настройки из файла
        with open(USER_CONFIG_PATH, 'r', encoding='utf-8') as f:
            self.config_data = yaml.safe_load(f) or {}
            
    def save_settings(self) -> None:
        """Сохраняет настройки в файл"""
        try:
            with open(USER_CONFIG_PATH, 'w', encoding='utf-8') as f:
                yaml.dump(self.config_data, f, default_flow_style=False, allow_unicode=True)
        except Exception as e:
            print(f"Ошибка сохранения конфигурации: {e}")
            
    def get_value(self, section: str, key: str, default: Any = None) -> Any:
        """Получает значение из настроек"""
        try:
            if section == "global":
                return self.config_data.get("global", {}).get(key.lower(), default)
            else:
                # Ищем в connections
                return self.config_data.get("connections", {}).get(section, {}).get(key.lower(), default)
        except Exception:
            return default
            
    def set_value(self, section: str, key: str, value: Any) -> None:
        """Устанавливает значение в настройках"""
        try:
            if section == "global":
                if "global" not in self.config_data:
                    self.config_data["global"] = {}
                self.config_data["global"][key.lower()] = value
            else:
                # Сохраняем в connections
                if "connections" not in self.config_data:
                    self.config_data["connections"] = {}
                if section not in self.config_data["connections"]:
                    self.config_data["connections"][section] = {}
                self.config_data["connections"][section][key.lower()] = value
            
            self.save_settings()
        except Exception as e:
            print(f"Ошибка установки значения: {e}")
            
    def get_backend_name(self) -> str:
        """Возвращает имя текущего бэкенда"""
        return self.get_value("global", "backend", "openai_over_proxy")
        
    def get_backend_config(self) -> Dict[str, Any]:
        """Возвращает конфигурацию текущего бэкенда"""
        backend_name = self.get_backend_name()
        return self.config_data.get("connections", {}).get(backend_name, {})

    def get_available_backends(self) -> list:
        """Возвращает список доступных бэкендов"""
        return list(self.config_data.get("connections", {}).keys())


# Создаем глобальный экземпляр настроек
settings = Settings()
