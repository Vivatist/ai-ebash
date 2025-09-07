#!/usr/bin/env python3
import sys
import json
import requests
from settings import API_URL, MODEL, CONTEXT, EXTRA_CONTEXT
import os
import subprocess
from formatter_text import format_answer

def get_system_context():
    """Подставляем реальные значения вместо $SHELL, $HOME, lsb_release"""
    try:
        ubuntu_version = subprocess.check_output(
            ["lsb_release", "-ds"], text=True
        ).strip()
    except Exception:
        ubuntu_version = "Ubuntu unknown"

    shell = os.environ.get("SHELL", "bash")
    home = os.environ.get("HOME", "/home/user")

    context = CONTEXT.replace("$(lsb_release -ds)", ubuntu_version)
    context = context.replace("$SHELL", shell).replace("$HOME", home)
    return context

def main():
    if len(sys.argv) < 2:
        print("Использование: ai [-run] ваш запрос к ИИ без кавычек")
        sys.exit(1)

    # Проверяем ключ -run
    run_mode = False
    args = sys.argv[1:]
    if "-run" in args:
        run_mode = True
        args.remove("-run")

    prompt = " ".join(args)

    system_context = get_system_context()
    full_context = system_context + "\n" + "\n".join(EXTRA_CONTEXT)

    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": full_context},
            {"role": "user", "content": prompt},
        ],
    }

    headers = {"Content-Type": "application/json"}

    try:
        response = requests.post(API_URL, headers=headers, data=json.dumps(payload))
        response.raise_for_status()
        data = response.json()

        if "choices" in data and len(data["choices"]) > 0:
            answer = data["choices"][0]["message"]["content"]
            formatted, code_blocks = format_answer(answer)
            print(formatted)

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
                            subprocess.run(code, shell=True)
                        else:
                            print("Нет такого блока.")
                    except KeyboardInterrupt:
                        print("\nВыход.")
                        break

        else:
            print("Ошибка: неожиданный формат ответа:", data)

    except requests.exceptions.HTTPError as e:
        print("HTTP ошибка:", e)
    except Exception as e:
        print("Ошибка:", e)

if __name__ == "__main__":
    main()
