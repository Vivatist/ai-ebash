from pathlib import Path
import yaml
import shutil
from typing import Dict, Any
from platformdirs import user_config_dir
from aiebash.logger import update_logger_config


# --- Пути к конфигурации ---
APP_NAME = "ai-ebash"
USER_CONFIG_DIR = Path(user_config_dir(APP_NAME))
USER_CONFIG_PATH = USER_CONFIG_DIR / "config.yaml"
DEFAULT_CONFIG_PATH = Path(__file__).parent / "default_config.yaml"


class ConfigManager:
    """Класс для работы с настройками приложения"""

    def __init__(self):
        self.config_data = {}
        self.load_settings()

    def load_settings(self) -> None:
        """Загружает настройки из файла или создает файл с настройками по умолчанию"""
        if not USER_CONFIG_PATH.exists():
            USER_CONFIG_DIR.mkdir(parents=True, exist_ok=True)
            if DEFAULT_CONFIG_PATH.exists():
                shutil.copy(DEFAULT_CONFIG_PATH, USER_CONFIG_PATH)

        try:
            with open(USER_CONFIG_PATH, 'r', encoding='utf-8') as f:
                self.config_data = yaml.safe_load(f) or {}
        except Exception:
            self.config_data = {}

        # Обновляем конфигурацию логгера
        update_logger_config(self.get_logging_config())

    def save_settings(self) -> None:
        """Сохраняет настройки в файл"""
        try:
            USER_CONFIG_DIR.mkdir(parents=True, exist_ok=True)
            with open(USER_CONFIG_PATH, 'w', encoding='utf-8') as f:
                yaml.dump(self.config_data, f, default_flow_style=False, allow_unicode=True)
        except Exception:
            pass

    def get_value(self, section: str, key: str, default: Any = None) -> Any:
        """Получает значение из настроек"""
        try:
            if section == "global":
                return self.config_data.get("global", {}).get(key, default)
            elif section == "logging":
                return self.config_data.get("logging", {}).get(key, default)
            else:
                # Ищем в supported_LLMs
                return self.config_data.get("supported_LLMs", {}).get(section, {}).get(key, default)
        except Exception:
            return default

    def get_logging_config(self) -> Dict[str, Any]:
        """Возвращает настройки логирования"""
        return self.config_data.get("logging", {})


# Создаем глобальный экземпляр
settings = ConfigManager()
