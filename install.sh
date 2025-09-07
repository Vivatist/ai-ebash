#!/usr/bin/env bash
set -e

# === Проверка root ===
if [[ $EUID -ne 0 ]]; then
   echo "❌ Запустите установку через sudo"
   exit 1
fi

echo "✅ Установка ai..."

# === Устанавливаем зависимости ===
apt update
apt install -y python3 python3-pip git

# === Устанавливаем Python-зависимости ===
pip3 install --upgrade pip
pip3 install requests

# === Копируем проект в /opt/ai-bash ===
INSTALL_DIR="/opt/ai-bash"
if [ -d "$INSTALL_DIR" ]; then
    echo "⚠️ Папка $INSTALL_DIR уже существует, удаляем..."
    rm -rf "$INSTALL_DIR"
fi
git clone https://github.com/Vivatist/ai-bash.git "$INSTALL_DIR"

# === Делаем обёртку ai в /usr/local/bin ===
cat > /usr/local/bin/ai <<'EOF'
#!/usr/bin/env bash
python3 /opt/ai-bash/ai.py "$@"
EOF

chmod +x /usr/local/bin/ai

echo "🎉 Установка завершена!"
echo "Теперь можно запускать: ai 'ваш запрос' из любой директории"
