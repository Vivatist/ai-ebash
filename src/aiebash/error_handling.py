import requests
from rich.console import Console

console = Console()

def handle_connection_error(error: Exception):
    """
    Обрабатывает типовые ошибки интернет соединения и выводит их в консоль.
    """
    if isinstance(error, requests.exceptions.ConnectionError):
        console.print("[dim]Ошибка соединения: не удалось подключиться к серверу. Проверьте интернет.[/dim]")
    elif isinstance(error, requests.exceptions.Timeout):
        console.print("[dim]Ошибка: время ожидания соединения истекло.[/dim]")
    elif isinstance(error, requests.exceptions.HTTPError):
        if hasattr(error, 'response') and error.response is not None:
            status_code = error.response.status_code
            if status_code == 403:
                console.print("[dim]Ошибка 403: Доступ запрещён\nВозможные причины:\n-Превышен лимит запросов (попробуйте через некоторое время)\n-Не поддерживается ваш регион (используйте VPN)[/dim]")
            elif status_code == 404:
                console.print("[dim]Ошибка 404: Ресурс не найден.[/dim]")
            elif status_code == 429:
                console.print("[dim]Ошибка 429: Слишком много запросов. Превышен лимит API. Попробуйте изменить параметры запроса или уменьшить частоту запросов.[/dim]")
            elif status_code == 401:
                console.print("[dim]Ошибка 401: Отказ в авторизации.Проверьте свой ключ API_KEY. Для получения ключа обратитесь к поставщику API. [link=https://github.com/Vivatist/ai-bash]Как получить ключ?[/link][/dim]")

            else:
                console.print(f"[dim]HTTP ошибка: {status_code}[/dim]")
        else:
            console.print("[dim]HTTP ошибка: неизвестная причина[/dim]")
    else:
        console.print(f"[dim]Неизвестная ошибка соединения: {error}[/dim]")
