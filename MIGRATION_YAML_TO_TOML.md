# Миграция с YAML на TOML

## Обзор изменений

Проект успешно переведен с использования YAML на TOML для конфигурационных файлов.

## Изменения в зависимостях

### setup.cfg и requirements.txt
- ❌ Удален: `pyyaml==6.0.2`
- ✅ Добавлен: `tomli>=1.2.0; python_version < "3.11"`
- ✅ Добавлен: `tomli-w>=1.0.0`

## Изменения в файлах

### Конфигурационные файлы
- ❌ `src/aiebash/default_config.yaml` → удален
- ✅ `src/aiebash/default_config.toml` → создан
- ❌ `~/.config/ai-ebash/config.yaml` → удален
- ✅ `~/.config/ai-ebash/config.toml` → создан

### Исходный код

#### config_manager.py
- Заменен импорт `import yaml` на `import tomllib`/`import tomli`
- Функция `_load_yaml_config()` → `_load_toml_config()`
- Функция `_save_yaml_config()` → `_save_toml_config()`
- Переменная `self.yaml_config` → `self.toml_config`
- Добавлена функция `_write_toml()` для записи TOML файлов

#### settings.py
- Заменен импорт `import yaml` на `import tomllib`/`import tomli`
- Функция загрузки обновлена для работы с бинарным режимом
- Добавлена функция `_write_toml()` для записи TOML файлов

## Формат TOML

### Преимущества TOML:
- ✅ Четкая спецификация
- ✅ Лучшая поддержка типов данных
- ✅ Более читаемый синтаксис
- ✅ Официальная поддержка в Python 3.11+

### Структура конфигурации:
```toml
[global]
context = "Системный контекст"
current_LLM = "openai_over_proxy"

[logging]
level = "DEBUG"
console_level = "CRITICAL"
file_level = "DEBUG"

[supported_LLMs.openai_over_proxy]
model = "gpt-4o-mini"
api_url = "https://api.openai.com/v1/chat/completions"
api_key = "your_api_key"

[supported_LLMs.openai]
model = "gpt-4o-mini"
api_url = "https://api.openai.com/v1/chat/completions"
api_key = "YOUR_API_KEY_HERE"
```

## Тестирование

Миграция протестирована и работает корректно:
- ✅ Чтение TOML файлов
- ✅ Запись TOML файлов
- ✅ Импорт модулей
- ✅ Работа с конфигурацией LLM

## Совместимость

- **Python 3.11+**: Используется встроенная библиотека `tomllib`
- **Python < 3.11**: Используется библиотека `tomli`
- **Запись TOML**: Используется `tomli-w` или встроенная функция

## Установка зависимостей

```bash
pip install tomli tomli-w
```

Или для Python 3.11+ достаточно:
```bash
pip install tomli-w
```