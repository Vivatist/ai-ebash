import subprocess
import platform
import tempfile
import os
from abc import ABC, abstractmethod
from rich.console import Console

from aiebash.logger import logger


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
        logger.debug(f"Выполнение bash-команды: {code_block[:80]}...")
        result = subprocess.run(
            code_block,
            shell=True,
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        logger.debug(f"Результат выполнения: код возврата {result.returncode}, "
                    f"stdout: {len(result.stdout)} байт, stderr: {len(result.stderr)} байт")
        return result


# Исполнитель команд для Windows
class WindowsCommandExecutor(CommandExecutor):
    """Исполнитель команд для Windows систем"""
    
    def execute(self, code_block: str) -> subprocess.CompletedProcess:
        """Выполняет bat-команды в Windows через временный файл"""
        # Предобработка кода для Windows
        code = code_block.replace('@echo off', '')
        code = code.replace('pause', 'rem pause')
        
        logger.debug(f"Подготовка Windows-команды: {code[:80]}...")
        
        # Создаем временный .bat файл
        fd, temp_path = tempfile.mkstemp(suffix='.bat')
        logger.debug(f"Создан временный файл: {temp_path}")
        
        try:
            with os.fdopen(fd, 'w') as f:
                f.write(code)
            
            # Запускаем с кодировкой консоли Windows
            logger.info(f"Выполнение команды из файла {temp_path}")
            result = subprocess.run(
                [temp_path],
                shell=True,
                capture_output=True,
                text=True,
                encoding='cp1251'  # Кириллическая кодировка для консоли Windows
            )
            logger.debug(f"Результат выполнения: код возврата {result.returncode}, "
                        f"stdout: {len(result.stdout)} байт, stderr: {len(result.stderr)} байт")
            return result
        except Exception as e:
            logger.error(f"Ошибка при выполнении Windows-команды: {e}", exc_info=True)
            raise
        finally:
            # Всегда удаляем временный файл
            try:
                os.unlink(temp_path)
                logger.debug(f"Временный файл {temp_path} удален")
            except Exception as e:
                logger.warning(f"Не удалось удалить временный файл {temp_path}: {e}")


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
        system = platform.system().lower()
        if system == "windows":
            logger.info("Создание исполнителя команд для Windows")
            return WindowsCommandExecutor()
        else:
            logger.info(f"Создание исполнителя команд для {system} (используется LinuxCommandExecutor)")
            return LinuxCommandExecutor()


def run_code_block(console: Console, code_blocks: list, idx: int) -> None:
    """
    Печатает номер и содержимое блока, выполняет его и выводит результат.
    
    Args:
        console (Console): Консоль для вывода
        code_blocks (list): Список блоков кода
        idx (int): Индекс выполняемого блока
    """
    logger.info(f"Запуск блока кода #{idx}")
    
    # Проверяем корректность индекса
    if not (1 <= idx <= len(code_blocks)):
        logger.warning(f"Некорректный индекс блока: {idx}. Доступно блоков: {len(code_blocks)}")
        console.print(f"[yellow]Блок #{idx} не существует. Доступны блоки с 1 по {len(code_blocks)}.[/yellow]")
        return
    
    code = code_blocks[idx - 1]
    logger.debug(f"Содержимое блока #{idx}: {code[:100]}...")
    
    console.print(f"\n>>> Выполняем блок #{idx}:", style="blue")
    console.print(code)
    
    # Получаем исполнитель для текущей ОС
    try:
        executor = CommandExecutorFactory.create_executor()
        
        # Выполняем код через соответствующий исполнитель
        logger.debug("Начало выполнения блока кода...")
        process = executor.execute(code)
                
        # Выводим результаты
        if process.stdout:
            logger.debug(f"Получен stdout ({len(process.stdout)} символов)")
            console.print(f"[green]>>>:[/green]\n{process.stdout}")
        else:
            console.print("[green]>>> Нет вывода stdout[/green]")
            
        if process.stderr:
            console.print(f"[yellow]>>>Error:[/yellow]\n{process.stderr}")
        
        # Добавляем информацию о статусе выполнения
        exit_code = process.returncode
        logger.info(f"Блок #{idx} выполнен с кодом {exit_code}")
        console.print(f"[blue]>>> Код завершения: {exit_code}[/blue]")
            
    except Exception as e:
        logger.error(f"Ошибка выполнения блока #{idx}: {e}", exc_info=True)
        console.print(f"[yellow]Ошибка выполнения скрипта: {e}[/yellow]")