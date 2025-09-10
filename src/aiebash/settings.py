import configparser
import shutil
from pathlib import Path
from platformdirs import user_config_dir
from typing import Optional  # <--- ДОБАВЛЕНО

# --- Пути к конфигурации ---
APP_NAME = "ai-ebash"
# Путь к конфигу пользователя (e.g., %APPDATA%\ai-ebash\config.ini)
USER_CONFIG_PATH = Path(user_config_dir(APP_NAME)) / "config.ini"
# Путь к дефолтному конфигу, который лежит рядом с этим файлом
DEFAULT_CONFIG_PATH = Path(__file__).parent / "default_config.ini"



# --- Логика инициализации ---
# Если у пользователя нет config.ini, копируем ему дефолтный
if not USER_CONFIG_PATH.exists():
    USER_CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(DEFAULT_CONFIG_PATH, USER_CONFIG_PATH)

# --- Чтение и предоставление доступа к настройкам ---
_config = configparser.ConfigParser()
_config.read(USER_CONFIG_PATH, encoding="utf-8")


class Settings:
    """Простая обертка для доступа к настройкам из config.ini."""
    def get(self, section: str, key: str, fallback: Optional[str] = None) -> Optional[str]: # <--- ИЗМЕНЕНО
        """Получить значение из [section] по ключу key."""
        return _config.get(section, key, fallback=fallback)

    def get_bool(self, section: str, key: str, fallback: bool = False) -> bool:
        """Получить булево значение."""
        return _config.getboolean(section, key, fallback=fallback)

# --- Экземпляр для всего проекта ---
# В других файлах импортируйте его: from aiebash.settings import settings
settings = Settings()


