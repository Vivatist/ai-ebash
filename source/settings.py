


API_URL = "https://openai-proxy.andrey-bch-1976.workers.dev/v1/chat/completions" # Прокси для OpenAI API
MODEL = "gpt-4o-mini"

# Основной контекст
CONTEXT = (
    "Ты помощник по Linux, особенно Ubuntu. "
    "Система Ubuntu $(lsb_release -ds), оболочка $SHELL. "
    "Домашняя директория $HOME. При ответе учитывай, что пользователь работает в терминале Bash."
)

# Дополнительный контекст
EXTRA_CONTEXT = [
    "Пользователь использует sudo",
    "Система подключена к интернету",
    "В системе установлены curl, jq, git"
]
