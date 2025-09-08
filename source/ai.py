#!/usr/bin/env python3
"""
ai.py — маленький CLI-клиент к API ИИ.
Запускается как: ai [-run] ваш запрос к ИИ
Опция -run позволяет выполнить предлагаемые код-блоки из ответа.
"""
import sys
import json
import subprocess
import requests
from rich.console import Console
from rich.markdown import Markdown

from settings import API_URL, MODEL, CONTEXT, DEBUG
from formatter_text import format_answer


def main():
    """Главная функция: парсит аргументы, формирует запрос к API и выводит ответ.
    
    Логика:
    - если нет аргументов — печатаем подсказку по использованию и выходим;
    - поддерживается флаг -run для интерактивного выполнения блоков кода
      из ответа ассистента.
    """
    if len(sys.argv) < 2:
        print("Использование: ai [-run] ваш запрос к ИИ без кавычек")
        sys.exit(0)

    # Проверяем ключ -run
    run_mode = False
    args = sys.argv[1:]
    if "-run" in args:
        run_mode = True
        args.remove("-run")

    # Собираем текст запроса из оставшихся аргументов
    prompt = " ".join(args)

    # Подготавливаем полезную нагрузку для API (стандартный формат chat-completions)
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": CONTEXT},
            {"role": "user", "content": prompt},
        ],
    }

    # Заголовки запроса
    headers = {"Content-Type": "application/json"}

    try:
        # Отправляем POST-запрос к API
        response = requests.post(API_URL, headers=headers, data=json.dumps(payload))
        response.raise_for_status()
        data = response.json()

        # Ожидаем формат ответа с choices -> message -> content
        if "choices" in data and len(data["choices"]) > 0:
            answer = data["choices"][0]["message"]["content"]

            # В режиме DEBUG выводим исходную (неформатированную) версию ответа
            if DEBUG:
                print("=== RAW RESPONSE ===")
                print(answer)
                print("=== /RAW RESPONSE ===\n")

            # format_answer разбивает текст на отформатированную часть
            # и список найденных блоков кода
            formatted, code_blocks = format_answer(answer)
            console = Console()
            console.print(Markdown(answer))

            # Если включён режим выполнения и есть блоки кода — предлагаем выбрать
            if run_mode and code_blocks:
                while True:
                    try:
                        choice = input("\nВведите номер блока для выполнения (0 - выход): ")
                        if not choice.isdigit():
                            print("Введите число.")
                            continue
                        choice = int(choice)
                        if choice == 0:
                            print("Выход.")
                            break
                        if 1 <= choice <= len(code_blocks):
                            code = code_blocks[choice - 1]
                            print(f"\n>>> Выполняем блок #{choice}:\n{code}\n")
                            # Выполняем выбранный блок в shell. Внимание: риск выполнения
                            # произвольного кода — используется на свой страх и риск.
                            subprocess.run(code, shell=True)
                        else:
                            print("Нет такого блока.")
                    except KeyboardInterrupt:
                        print("\nВыход.")
                        break

        else:
            # Непредвиденный формат ответа — выводим для отладки
            print("Ошибка: неожиданный формат ответа:", data)

    except requests.exceptions.HTTPError as e:
        # Ошибки уровня HTTP (4xx/5xx)
        print("HTTP ошибка:", e)
    except Exception as e:
        # Прочие ошибки (сеть, JSON, и т.д.)
        print("Ошибка:", e)

if __name__ == "__main__":
    main()
