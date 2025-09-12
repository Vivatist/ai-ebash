import subprocess
import platform
import tempfile
import os
from abc import ABC, abstractmethod
from rich.console import Console

# Абстрактный базовый класс для исполнителей команд
class CommandExecutor(ABC):
    """Базовый интерфейс для исполнителей команд разных ОС"""
    
    @abstractmethod
    def execute(self, code_block: str) -> subprocess.CompletedProcess:
        """
        Выполняет блок кода и возвращает результат
        
        Args:
            code_block (str): Блок кода для выполнения
            
        Returns:
            subprocess.CompletedProcess: Результат выполнения команды
        """
        pass


# Исполнитель команд для Linux
class LinuxCommandExecutor(CommandExecutor):
    """Исполнитель команд для Linux/Unix систем"""
    
    def execute(self, code_block: str) -> subprocess.CompletedProcess:
        """Выполняет bash-команды в Linux"""
        return subprocess.run(
            code_block,
            shell=True,
            capture_output=True,
            text=True,
            encoding='utf-8'
        )


# Исполнитель команд для Windows
class WindowsCommandExecutor(CommandExecutor):
    """Исполнитель команд для Windows систем"""
    
    def execute(self, code_block: str) -> subprocess.CompletedProcess:
        """Выполняет bat-команды в Windows через временный файл"""
        # Предобработка кода для Windows
        code = code_block.replace('@echo off', '')
        code = code.replace('pause', 'rem pause')
        
        # Создаем временный .bat файл
        fd, temp_path = tempfile.mkstemp(suffix='.bat')
        try:
            with os.fdopen(fd, 'w') as f:
                f.write(code)
            
            # Запускаем с кодировкой консоли Windows
            result = subprocess.run(
                [temp_path],
                shell=True,
                capture_output=True,
                text=True,
                encoding='cp866'  # Кириллическая кодировка для консоли Windows
            )
            return result
        finally:
            # Всегда удаляем временный файл
            try:
                os.unlink(temp_path)
            except:
                pass


# Фабрика для создания исполнителей команд
class CommandExecutorFactory:
    """Фабрика для создания исполнителей команд в зависимости от ОС"""
    
    @staticmethod
    def create_executor() -> CommandExecutor:
        """
        Создает исполнитель команд в зависимости от текущей ОС
        
        Returns:
            CommandExecutor: Соответствующий исполнитель для текущей ОС
        """
        if platform.system().lower() == "windows":
            return WindowsCommandExecutor()
        else:
            return LinuxCommandExecutor()


def run_code_block(console: Console, code_blocks: list, idx: int) -> None:
    """
    Печатает номер и содержимое блока, выполняет его и выводит результат.
    
    Args:
        console (Console): Консоль для вывода
        code_blocks (list): Список блоков кода
        idx (int): Индекс выполняемого блока
    """
    console.print(f"\n>>> Выполняем блок #{idx}:", style="blue")
    console.print(code_blocks[idx - 1])
    
    # Получаем исполнитель для текущей ОС
    executor = CommandExecutorFactory.create_executor()
    
    try:
        # Выполняем код через соответствующий исполнитель
        process = executor.execute(code_blocks[idx - 1])
        
        # Выводим результаты
        if process.stdout:
            console.print(f"[green]>>>:[/green]\n{process.stdout}")
        else:
            console.print("[green]>>> Нет вывода stdout[/green]")
            
        if process.stderr:
            console.print(f"[yellow]>>>Error:[/yellow]\n{process.stderr}")
        
        # Добавляем информацию о статусе выполнения
        console.print(f"[blue]>>> Код завершения: {process.returncode}[/blue]")
            
    except Exception as e:
        console.print(f"[yellow]Ошибка выполнения скрипта: {e}[/yellow]")