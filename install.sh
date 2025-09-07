#!/usr/bin/env bash
set -e

echo "✅ Установка ai-bash через pipx..."

# === Проверка sudo только для apt install ===
if [[ $EUID -ne 0 ]]; then
    echo "ℹ️ Для установки системных зависимостей потребуется sudo."
fi

# === Устанавливаем системные зависимости ===
sudo apt update
sudo apt install -y python3 python3-venv python3-pip pipx git

# === Убедимся, что pipx добавлен в PATH для текущего пользователя ===
pipx ensurepath

LOCAL_BIN="$HOME/.local/bin"
PROFILE_FILE="$HOME/.profile"

if [[ ":$PATH:" != *":$LOCAL_BIN:"* ]]; then
    echo "⚠ Добавляем $LOCAL_BIN в PATH через $PROFILE_FILE..."
    echo "" >> "$PROFILE_FILE"
    echo "# Добавляем pipx и локальные бинарники в PATH" >> "$PROFILE_FILE"
    echo "export PATH=\"$LOCAL_BIN:\$PATH\"" >> "$PROFILE_FILE"
    export PATH="$LOCAL_BIN:$PATH"
    echo "✅ PATH обновлён. Перезапустите терминал для полной активации."
fi

# === Клонируем проект в /opt/ai-bash ===
INSTALL_DIR="/opt/ai-bash"
if [ -d "$INSTALL_DIR" ]; then
    echo "🔄 Обновление существующего проекта..."
    sudo rm -rf "$INSTALL_DIR"
fi
sudo git clone https://github.com/Vivatist/ai-bash.git "$INSTALL_DIR"
sudo chown -R $USER:$USER "$INSTALL_DIR"

# === Устанавливаем пакет через pipx (без sudo!) ===
pipx install --force "$INSTALL_DIR"

echo "🎉 Установка завершена!"
echo "Теперь можно запускать: ai 'ваш запрос'"
echo "Если терминал не видит команду ai, закройте его и откройте снова, или выполните: source ~/.profile"
