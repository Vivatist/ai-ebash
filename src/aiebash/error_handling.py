import requests
from rich.console import Console

console = Console()

def handle_connection_error(error: Exception):
    """
    Обрабатывает типовые ошибки интернет соединения и выводит их в консоль.
    """
    if isinstance(error, requests.exceptions.ConnectionError):
        console.print("[yellow]Ошибка соединения: не удалось подключиться к серверу. Проверьте интернет.[/yellow]")
    elif isinstance(error, requests.exceptions.Timeout):
        console.print("[yellow]Ошибка: время ожидания соединения истекло.[/yellow]")
    elif isinstance(error, requests.exceptions.HTTPError):
        if hasattr(error, 'response') and error.response is not None:
            status_code = error.response.status_code
            if status_code == 403:
                console.print("[yellow]Ошибка 403: Доступ запрещён (Forbidden). Проверьте API ключ или права доступа.[/yellow]")
            elif status_code == 404:
                console.print("[yellow]Ошибка 404: Ресурс не найден.[/yellow]")
            else:
                console.print(f"[yellow]HTTP ошибка: {status_code}[/yellow]")
        else:
            console.print("[yellow]HTTP ошибка: неизвестная причина[/yellow]")
    else:
        console.print(f"[yellow]Неизвестная ошибка соединения: {error}[/yellow]")
