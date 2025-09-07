#!/usr/bin/env bash
set -e

echo "✅ Установка ai через pipx..."

# Проверка root
if [[ $EUID -ne 0 ]]; then
   echo "❌ Запустите установку через sudo"
   exit 1
fi

# === Устанавливаем системные зависимости ===
apt update
apt install -y python3 python3-venv python3-pip pipx git

# === Убедимся, что pipx добавлен в PATH ===
pipx ensurepath

# === Проверяем ~/.local/bin в PATH через .profile ===
LOCAL_BIN="$HOME/.local/bin"
PROFILE_FILE="$HOME/.profile"

if ! grep -q "$LOCAL_BIN" "$PROFILE_FILE" 2>/dev/null; then
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
    rm -rf "$INSTALL_DIR"
fi
git clone https://github.com/Vivatist/ai-bash.git "$INSTALL_DIR"

# === Устанавливаем пакет через pipx ===
pipx install --force "$INSTALL_DIR"

echo "🎉 Установка завершена!"
echo "Теперь можно запускать: ai 'ваш запрос'"
