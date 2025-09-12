from pathlib import Path
import yaml
import os
import shutil
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
            
            # Проверяем наличие файла дефолтного конфига
            if DEFAULT_CONFIG_PATH.exists():
                shutil.copy(DEFAULT_CONFIG_PATH, USER_CONFIG_PATH)
            else:
                return 
        
        # Загружаем настройки из файла
        try:
            with open(USER_CONFIG_PATH, 'r', encoding='utf-8') as f:
                self.config_data = yaml.safe_load(f) or {}
        except Exception:
            self.config_data = {}
            
    def save_settings(self) -> None:
        """Сохраняет настройки в файл"""
        try:
            # Создаем директорию, если ее нет
            USER_CONFIG_DIR.mkdir(parents=True, exist_ok=True)
            
            with open(USER_CONFIG_PATH, 'w', encoding='utf-8') as f:
                yaml.dump(self.config_data, f, default_flow_style=False, allow_unicode=True)
        except Exception:
            pass
            
    def get_value(self, section: str, key: str, default: Any = None) -> Any:
        """Получает значение из настроек"""
        try:
            if section == "global":
                value = self.config_data.get("global", {}).get(key.lower(), default)
                return value
            else:
                # Ищем в connections
                value = self.config_data.get("connections", {}).get(section, {}).get(key.lower(), default)
                return value
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
        except Exception:
            pass
            
    def get_backend_name(self) -> str:
        """Возвращает имя текущего бэкенда"""
        backend = self.get_value("global", "backend", "openai_over_proxy")
        return backend
        
    def get_backend_config(self) -> Dict[str, Any]:
        """Возвращает конфигурацию текущего бэкенда"""
        backend_name = self.get_backend_name()
        config = self.config_data.get("connections", {}).get(backend_name, {})
        return config

    def get_available_backends(self) -> list:
        """Возвращает список доступных бэкендов"""
        backends = list(self.config_data.get("connections", {}).keys())
        return backends
    
    def get_logging_config(self) -> Dict[str, Any]:
        """
        Возвращает настройки логирования из конфигурации.
        
        Returns:
            Dict[str, Any]: Настройки логирования
        """
        return self.config_data.get("global", {}).get("logging", {})


# Создаем глобальный экземпляр настроек
settings = Settings()
