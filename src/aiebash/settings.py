
from pathlib import Path
import configparser
from platformdirs import user_config_dir

APP_NAME = "ai-bash"

# Дефолтные значения хранятся в словаре
DEFAULTS = {
    "API_URL": "https://openai-proxy.andrey-bch-1976.workers.dev/v1/chat/completions", # Прокси для OpenAI API
    "API_KEY": "",  # Ключ API (если нужен) 
    "MODEL": "gpt-4o-mini", # Модель по умолчанию
    "CONTEXT": ( # Контекст по умолчанию
        "Ты профессиональный системный администратор, помощник по Linux. "
        "Пользователь - новичок в Linux, помоги ему. "
        "Система Ubuntu, оболочка $SHELL. "
        "При ответе учитывай, что пользователь работает в терминале Bash."
        "Отвечай всегда на русском языке. "
        "Ты разговариваешь с пользователем в терминале. "
    ), 
    "DEBUG": False  # Включить отладочную информацию
}

# Где хранится INI-файл
# Ubuntu → ~/.config/ai-bash/config.ini
# Windows → C:\Users\<user>\AppData\Local\ai-bash\ai-bash\config.ini

class Settings:
    def __init__(self):
        # Кроссплатформенная директория конфигов
        self.config_dir = Path(user_config_dir(APP_NAME))
        self.config_dir.mkdir(parents=True, exist_ok=True)

        self.config_file = self.config_dir / "config.ini"
        self.config = configparser.ConfigParser()

        # Если файл есть — читаем, иначе создаём с дефолтами
        if self.config_file.exists():
            self.config.read(self.config_file)
            if "settings" not in self.config:
                self.config["settings"] = DEFAULTS
                self._save()
        else:
            self.config["settings"] = DEFAULTS
            self._save()
            print(f"[INFO] Создан новый конфиг: {self.config_file}")

    def _save(self):
        with open(self.config_file, "w") as f:
            self.config.write(f)

    # Получение значений
    def get(self, key):
        return self.config["settings"].get(key, DEFAULTS.get(key))

    # Изменение значений
    def set(self, key, value):
        self.config["settings"][key] = str(value)
        self._save()


# Глобальный объект настроек
settings = Settings()


