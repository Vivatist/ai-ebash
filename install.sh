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

# === Клонируем проект в /opt/ai-bash ===
INSTALL_DIR="/opt/ai-bash"
if [ -d "$INSTALL_DIR" ]; then
    echo "🔄 Обновление существующего проекта..."
    rm -rf "$INSTALL_DIR"
fi
git clone https://github.com/Vivatist/ai-bash.git "$INSTALL_DIR"

# === Устанавливаем пакет через pipx ===
pipx install --force "$INSTALL_DIR"

# === Проверяем PATH ===
if ! command -v ai &> /dev/null; then
    echo "⚠ ai не найден в PATH. Добавляем ~/.local/bin в PATH..."
    SHELL_RC="$HOME/.bashrc"
    if [ -n "$ZSH_VERSION" ]; then
        SHELL_RC="$HOME/.zshrc"
    fi
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$SHELL_RC"
    echo "✅ PATH обновлён. Перезапустите терминал или выполните:"
    echo "source $SHELL_RC"
fi

echo "🎉 Установка завершена!"
echo "Теперь можно запускать: ai 'ваш запрос'"
