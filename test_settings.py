#!/usr/bin/env python3
"""
Простой тест интерактивного режима настройки
"""

import sys
from pathlib import Path

# Добавляем src в путь
sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from aiebash.config_manager import run_configuration_dialog

if __name__ == "__main__":
    print("Запуск теста интерактивной настройки...")
    try:
        run_configuration_dialog()
        print("Тест завершен успешно")
    except KeyboardInterrupt:
        print("\nТест прерван пользователем")
    except Exception as e:
        print(f"Ошибка в тесте: {e}")
        import traceback
        traceback.print_exc()