#!/usr/bin/env bash
set -e

echo "✅ Установка ai через pipx..."

# Проверка sudo для apt install
if [[ $EUID -ne 0 ]]; then
   echo "❌ Запустите установку через sudo"
   exit 1
fi

# === Устанавливаем системные зависимости ===
apt update
apt install -y python3 python3-venv python3-pip pipx git

# === Убедимся, что pipx добавлен в PATH ===
pipx ensurepath

# === Проверяем PATH пользователя и добавляем ~/.local/bin, если нужно ===
LOCAL_BIN="$HOME/.local/bin"
SHELL_RC="$HOME/.bashrc"
if [ -n "$ZSH_VERSION" ]; then
    SHELL_RC="$HOME/.zshrc"
fi

if [[ ":$PATH:" != *":$LOCAL_BIN:"* ]]; then
    echo "⚠ ~/.local/bin не в PATH, добавляем..."
    echo "export PATH=\"$LOCAL_BIN:\$PATH\"" >> "$SHELL_RC"
    export PATH="$LOCAL_BIN:$PATH"
    echo "✅ PATH обновлён. Перезапустите терминал, если команда ai не найдётся."
fi

# === Клонируем проект в /opt/ai-bash ===
INSTALL_DIR="/opt/ai-bash"
if [ -d "$INSTALL_DIR" ]; then
    echo "🔄 Обновление существующего проекта..."
    rm -rf "$INSTALL_DIR"
fi
git clone https://github.com/Vivatist/ai-bash.git "$INSTALL_DIR"

# === Устанавливаем пакет через pipx ===
pipx install --force "$INSTALL_DIR"

echo "🎉 Установка завершена!"
echo "Теперь можно запускать: ai 'ваш запрос'"
