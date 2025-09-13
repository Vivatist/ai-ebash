#!/usr/bin/env python3
"""
Тест миграции с YAML на TOML
"""

import sys
import os
from pathlib import Path

# Добавляем src в путь
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_toml_migration():
    """Тестирование миграции на TOML"""
    print("🧪 Тестирование миграции с YAML на TOML")
    print()

    try:
        # Импорт TOML библиотек
        try:
            import tomllib  # Python 3.11+
            print("✅ Используется встроенная библиотека tomllib (Python 3.11+)")
        except ImportError:
            import tomli as tomllib  # Python < 3.11
            print("✅ Используется библиотека tomli (Python < 3.11)")

        # Проверка наличия конфигурационных файлов
        default_config = Path("src/aiebash/default_config.toml")
        user_config = Path.home() / ".config" / "ai-ebash" / "config.toml"

        if default_config.exists():
            print(f"✅ Найден файл конфигурации по умолчанию: {default_config}")
        else:
            print(f"❌ Не найден файл конфигурации по умолчанию: {default_config}")

        if user_config.exists():
            print(f"✅ Найден пользовательский файл конфигурации: {user_config}")
        else:
            print(f"⚠ Не найден пользовательский файл конфигурации: {user_config}")

        # Тест чтения TOML файла
        print("\n📖 Тестирование чтения TOML файла...")
        try:
            with open(default_config, 'rb') as f:
                config_data = tomllib.load(f)
            print("✅ TOML файл успешно прочитан")
            print(f"   Ключи верхнего уровня: {list(config_data.keys())}")

            if 'supported_LLMs' in config_data:
                llms = list(config_data['supported_LLMs'].keys())
                print(f"   Доступные LLM: {llms}")

        except Exception as e:
            print(f"❌ Ошибка чтения TOML файла: {e}")

        # Тест импорта модулей
        print("\n📦 Тестирование импорта модулей...")
        try:
            from aiebash.config_manager import config_manager
            print("✅ Модуль config_manager успешно импортирован")

            # Тест получения доступных LLM
            available_llms = config_manager.get_available_llms()
            print(f"✅ Доступные LLM: {available_llms}")

            # Тест получения текущего LLM
            current_llm = config_manager.get_current_llm_name()
            print(f"✅ Текущий LLM: {current_llm}")

        except Exception as e:
            print(f"❌ Ошибка импорта модулей: {e}")

        print("\n🎉 Тестирование миграции завершено!")

    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_toml_migration()