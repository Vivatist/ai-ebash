# ...existing code...
#!/usr/bin/env bash
set -e

# === Проверка root ===
if [[ $EUID -ne 0 ]]; then
   echo "Запустите установку через sudo"
   exit 1
fi

echo "Установка/обновление ai..."

# === Проверка системных зависимостей ===
for cmd in python3 git; do
    if ! command -v $cmd &>/dev/null; then
        echo "Устанавливаем $cmd..."
        apt update
        apt install -y $cmd
    fi
done

# === Директория установки ===
INSTALL_DIR="/opt/ai-bash"

if [ -d "$INSTALL_DIR" ]; then
    echo "Папка $INSTALL_DIR уже существует. Обновляем проект..."
    cd "$INSTALL_DIR"
    git reset --hard
    git pull
else
    git clone https://github.com/Vivatist/ai-bash.git "$INSTALL_DIR"
    cd "$INSTALL_DIR"
fi

# === Виртуальное окружение ===
if [ ! -d "$INSTALL_DIR/venv" ]; then
    echo "Создаём виртуальное окружение..."
    python3 -m venv "$INSTALL_DIR/venv"
fi

# === Обновляем pip и устанавливаем зависимости из requirements.txt ===
"$INSTALL_DIR/venv/bin/pip" install --upgrade pip

REQ_FILE="$INSTALL_DIR/requirements.txt"

if [ -f "$REQ_FILE" ]; then
    echo "Устанавливаем зависимости из $REQ_FILE..."
    "$INSTALL_DIR/venv/bin/pip" install -r "$REQ_FILE"
else
    echo "Файл source/requirements.txt не найден в $INSTALL_DIR. Создайте файл с зависимостями."
    exit 1
fi

# === Создаём обёртку ai в /usr/local/bin (точка входа в source/) ===
cat > /usr/local/bin/ai <<EOF
#!/usr/bin/env bash
"$INSTALL_DIR/venv/bin/python" "$INSTALL_DIR/source/ai.py" "\$@"
EOF

chmod +x /usr/local/bin/ai

# === Завершение ===
echo "Установка / обновление завершено."
echo "Теперь вы можете запускать команду ai из любой директории:"
echo "   ai 'ваш запрос к ИИ'"
echo ""
echo "Если команда не найдена, перезапустите терминал или выполните:"
echo "   source ~/.bashrc  # или аналогично для вашей оболочки"
# ...existing code...