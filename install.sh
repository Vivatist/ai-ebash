#!/usr/bin/env bash
set -e

echo "✅ Установка ai через pipx..."

# === Проверка sudo ===
if [[ $EUID -ne 0 ]]; then
   echo "❌ Запустите установку через sudo"
   exit 1
fi

# === Устанавливаем зависимости системы ===
apt update
apt install -y python3 python3-venv python3-pip pipx git

# Убедимся, что pipx добавлен в PATH
pipx ensurepath

# === Устанавливаем проект через pipx ===
# Если уже установлен — обновляем
if pipx list | grep -q ai-bash; then
    echo "🔄 Обновление ai-bash через pipx..."
    pipx upgrade git+https://github.com/Vivatist/ai-bash.git
else
    echo "📦 Установка ai-bash через pipx..."
    pipx install git+https://github.com/Vivatist/ai-bash.git
fi

echo "🎉 Установка завершена!"
echo "Теперь можно запускать: ai 'ваш запрос'"
echo "Пример: ai 'Напиши скрипт на bash для резервного копирования файлов'"