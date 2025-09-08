#!/usr/bin/env python3
"""
ai.py — маленький CLI-клиент к API ИИ.
Запускается как: ai [-run] ваш запрос к ИИ
Опция -run позволяет выполнить предлагаемые код-блоки из ответа.
"""
import sys
import json
import requests
from settings import API_URL, MODEL, CONTEXT, EXTRA_CONTEXT
import os
import subprocess
from formatter_text import format_answer

def get_system_context():
    """Подставляем реальные значения вместо $SHELL, $HOME, $(lsb_release -ds)
    
    Возвращает строку контекста для системной роли (подставляет данные окружения
    и версию дистрибутива в шаблон CONTEXT из settings).
    """
    try:
        # Пытаемся получить информацию о дистрибутиве Ubuntu
        ubuntu_version = subprocess.check_output(
            ["lsb_release", "-ds"], text=True
        ).strip()
    except Exception:
        # Если команда недоступна — используем запасное значение
        ubuntu_version = "Ubuntu unknown"

    # Берём SHELL и HOME из окружения, если отсутствуют — ставим разумные значения
    shell = os.environ.get("SHELL", "bash")
    home = os.environ.get("HOME", "/home/user")

    # Подставляем значения в шаблон CONTEXT
    context = CONTEXT.replace("$(lsb_release -ds)", ubuntu_version)
    context = context.replace("$SHELL", shell).replace("$HOME", home)
    return context

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

    # Формируем системный контекст и объединяем с дополнительным из settings
    system_context = get_system_context()
    full_context = system_context + "\n" + "\n".join(EXTRA_CONTEXT)

    # Подготавливаем полезную нагрузку для API (стандартный формат chat-completions)
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": full_context},
            {"role": "user", "content": prompt},
        ],
    }

    # Заголовки запроса (здесь нет Authorization — ключ должен быть добавлен в settings/в другом месте)
    headers = {"Content-Type": "application/json"}

    try:
        # Отправляем POST-запрос к API
        response = requests.post(API_URL, headers=headers, data=json.dumps(payload))
        response.raise_for_status()
        data = response.json()

        # Ожидаем формат ответа с choices -> message -> content
        if "choices" in data and len(data["choices"]) > 0:
            answer = data["choices"][0]["message"]["content"]
            # formatter_text.format_answer разбивает текст на отформатированную часть
            # и список найденных блоков кода
            formatted, code_blocks = format_answer(answer)
            print(formatted)

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
