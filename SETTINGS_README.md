# Интерактивная настройка ai-ebash

Модуль `config_manager.py` предоставляет интерактивную систему настройки приложения с использованием Dynaconf.

## Возможности

- **Интерактивная настройка**: Последовательное прохождение по всем глобальным настройкам
- **Управление LLM**: Добавление, удаление и выбор LLM из списка supported_LLMs
- **Безопасность**: Напоминание о переносе API ключей в переменные окружения
- **Совместимость**: Поддержка старого API для обратной совместимости

## Использование

### Интерактивный режим
```bash
python -m aiebash --settings
# или
ai --settings
```

### Программное использование
```python
from aiebash.config_manager import config_manager, run_interactive_setup

# Получение значений
context = config_manager.get_value("global", "context")
model = config_manager.get_value("openai_over_proxy", "model")

# Установка значений
config_manager.set_value("global", "context", "Новый контекст")

# Запуск интерактивной настройки
run_interactive_setup()
```

## Структура конфигурации

```yaml
global:
  context: "Системный контекст"
  current_LLM: openai_over_proxy

logging:
  level: DEBUG
  console_level: CRITICAL
  file_level: DEBUG

supported_LLMs:
  openai_over_proxy:
    model: gpt-4o-mini
    api_url: https://api.example.com
    api_key: ""
```

## Безопасность

⚠️ **Важно**: API ключи хранятся в открытом виде в config.yaml

Рекомендации:
- Используйте переменные окружения: `export AIEBASH_OPENAI_API_KEY=your_key`
- Установите права доступа только для владельца
- Не коммитите ключи в git

## API

### ConfigManager

- `get_value(section, key, default)` - получение значения
- `set_value(section, key, value)` - установка значения
- `get_logging_config()` - получение настроек логирования
- `get_current_llm_name()` - имя текущего LLM
- `get_current_llm_config()` - конфигурация текущего LLM
- `get_available_llms()` - список доступных LLM
- `run_interactive_setup()` - запуск интерактивной настройки

### Функции совместимости

- `get_value(section, key, default)`
- `set_value(section, key, value)`
- `get_logging_config()`
- `run_interactive_setup()`