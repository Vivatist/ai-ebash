#!/usr/bin/env bash
set -e

# === Проверка root ===
if [[ $EUID -ne 0 ]]; then
   echo "Запустите удаление через sudo"
   exit 1
fi

INSTALL_DIR="/opt/ai-bash"
WRAPPER="/usr/local/bin/ai"

echo "Удаление ai..."

# === Удаляем обёртку ===
if [ -f "$WRAPPER" ]; then
    rm "$WRAPPER"
    echo "Удалён файл обёртки $WRAPPER"
else
    echo "Файл обёртки $WRAPPER не найден"
fi

# === Удаляем проект и виртуальное окружение ===
if [ -d "$INSTALL_DIR" ]; then
    rm -rf "$INSTALL_DIR"
    echo "Удалена директория $INSTALL_DIR"
else
    echo "Директория $INSTALL_DIR не найдена"
fi

echo "Удаление завершено. Команда ai больше не доступна."
