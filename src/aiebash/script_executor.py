"""
Модуль для выполнения блоков кода в различных операционных системах.

Поддерживает:
- Linux/Unix системы через bash
- Windows системы через временные .bat файлы
- Вывод в реальном времени с правильной обработкой кодировок
"""
import subprocess
import platform
import tempfile
import os
import sys
from abc import ABC, abstractmethod
from typing import List, Optional
from rich.console import Console
from aiebash.i18n import t
from aiebash.logger import logger, log_execution_time


class CommandExecutor(ABC):
    """Базовый интерфейс для исполнителей команд разных ОС."""
    
    @abstractmethod
    def execute(self, code_block: str) -> subprocess.CompletedProcess:
        """
        Выполняет блок кода и возвращает результат.
        
        Args:
            code_block: Блок кода для выполнения
            
        Returns:
            Результат выполнения команды
        """
        pass

    def _decode_output_line(self, line_bytes: bytes, encodings: List[str]) -> str:
        """
        Безопасно декодирует строку из байтов, пробуя различные кодировки.
        
        Args:
            line_bytes: Байты для декодирования
            encodings: Список кодировок для попытки
            
        Returns:
            Декодированная строка
        """
        for encoding in encodings:
            try:
                return line_bytes.decode(encoding, errors='strict').strip()
            except UnicodeDecodeError:
                continue
        
        # Fallback: используем замену с ошибками
        try:
            return line_bytes.decode('utf-8', errors='replace').strip()
        except Exception:
            return line_bytes.decode('latin1', errors='replace').strip()

    def _process_output_stream(self, stream, output_lines: List[str], 
                              encodings: List[str], is_stderr: bool = False) -> None:
        """
        Обрабатывает поток вывода в реальном времени.
        
        Args:
            stream: Поток для чтения
            output_lines: Список для сохранения строк
            encodings: Кодировки для декодирования
            is_stderr: Является ли поток stderr
        """
        if not stream:
            return
            
        for line in stream:
            if not line:
                continue
                
            decoded_line = self._decode_output_line(line, encodings)
            if not decoded_line:
                continue
                
            output_lines.append(decoded_line)
            
            if is_stderr:
                print(t("Error: {line}").format(line=decoded_line), file=sys.stderr)
            else:
                print(decoded_line)


class LinuxCommandExecutor(CommandExecutor):
    """Исполнитель команд для Linux/Unix систем."""
    
    UNIX_ENCODINGS = ['utf-8', 'iso-8859-1', 'ascii']
    
    @log_execution_time
    def execute(self, code_block: str) -> subprocess.CompletedProcess:
        """Выполняет bash-команды в Linux с выводом в реальном времени."""
        logger.debug(f"Executing bash command: {code_block[:80]}...")
        
        process = subprocess.Popen(
            code_block,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=False
        )
        
        stdout_lines = []
        stderr_lines = []
        
        # Обрабатываем stdout
        self._process_output_stream(
            process.stdout, stdout_lines, self.UNIX_ENCODINGS, is_stderr=False
        )
        
        # TODO: Обработка stderr временно отключена
        # self._process_output_stream(
        #     process.stderr, stderr_lines, self.UNIX_ENCODINGS, is_stderr=True
        # )
        
        process.wait()
        
        result = subprocess.CompletedProcess(
            args=code_block,
            returncode=process.returncode,
            stdout='\n'.join(stdout_lines) if stdout_lines else '',
            stderr='\n'.join(stderr_lines) if stderr_lines else ''
        )
        
        self._log_execution_result(result)
        return result
        
    def _log_execution_result(self, result: subprocess.CompletedProcess) -> None:
        """Логирует результат выполнения команды."""
        logger.debug(
            t("Execution result: return code {code}, stdout: {stdout} bytes, "
              "stderr: {stderr} bytes").format(
                code=result.returncode,
                stdout=len(result.stdout) if result.stdout else 0,
                stderr=len(result.stderr) if result.stderr else 0,
            )
        )


class WindowsCommandExecutor(CommandExecutor):
    """Исполнитель команд для Windows систем."""
    
    WINDOWS_ENCODINGS = ['cp866', 'cp1251', 'utf-8', 'ascii']
    BATCH_FILE_ENCODING = 'cp1251'
    
    @log_execution_time
    def execute(self, code_block: str) -> subprocess.CompletedProcess:
        """Выполняет bat-команды в Windows через временный файл."""
        preprocessed_code = self._preprocess_windows_code(code_block)
        temp_path = self._create_temporary_batch_file(preprocessed_code)
        
        try:
            return self._execute_batch_file(temp_path)
        finally:
            self._cleanup_temporary_file(temp_path)
    
    def _preprocess_windows_code(self, code_block: str) -> str:
        """Предобрабатывает код для Windows."""
        code = code_block.replace('@echo off', '')
        code = code.replace('pause', 'rem pause')
        logger.debug(f"Preprocessing Windows command: {code[:80]}...")
        return code
    
    def _create_temporary_batch_file(self, code: str) -> str:
        """Создает временный .bat файл с правильной кодировкой."""
        fd, temp_path = tempfile.mkstemp(suffix='.bat')
        logger.debug(f"Created temporary file: {temp_path}")
        
        with os.fdopen(fd, 'w', encoding=self.BATCH_FILE_ENCODING, errors='replace') as f:
            f.write(code)
        
        return temp_path
    
    def _execute_batch_file(self, temp_path: str) -> subprocess.CompletedProcess:
        """Выполняет .bat файл и возвращает результат."""
        logger.info(f"Executing command from file {temp_path}")
        
        process = subprocess.Popen(
            [temp_path],
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=False,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        
        stdout_lines = []
        stderr_lines = []
        
        # Обрабатываем потоки вывода
        self._process_output_stream(
            process.stdout, stdout_lines, self.WINDOWS_ENCODINGS, is_stderr=False
        )
        self._process_output_stream(
            process.stderr, stderr_lines, self.WINDOWS_ENCODINGS, is_stderr=True
        )
        
        process.wait()
        
        result = subprocess.CompletedProcess(
            args=[temp_path],
            returncode=process.returncode,
            stdout='\n'.join(stdout_lines) if stdout_lines else '',
            stderr='\n'.join(stderr_lines) if stderr_lines else ''
        )
        
        self._log_execution_result(result)
        return result
    
    def _log_execution_result(self, result: subprocess.CompletedProcess) -> None:
        """Логирует результат выполнения команды."""
        logger.debug(
            t("Execution result: return code {code}, stdout: {stdout} bytes, "
              "stderr: {stderr} bytes").format(
                code=result.returncode,
                stdout=len(result.stdout) if result.stdout else 0,
                stderr=len(result.stderr) if result.stderr else 0,
            )
        )
    
    def _cleanup_temporary_file(self, temp_path: str) -> None:
        """Удаляет временный файл."""
        try:
            os.unlink(temp_path)
            logger.debug(f"Temporary file {temp_path} deleted")
        except Exception as e:
            logger.warning(f"Failed to delete temporary file {temp_path}: {e}")


class CommandExecutorFactory:
    """Фабрика для создания исполнителей команд в зависимости от ОС."""
    
    @staticmethod
    @log_execution_time
    def create_executor() -> CommandExecutor:
        """
        Создает исполнитель команд в зависимости от текущей ОС.
        
        Returns:
            Соответствующий исполнитель для текущей ОС
        """
        system = platform.system().lower()
        
        if system == "windows":
            logger.info("Creating command executor for Windows")
            return WindowsCommandExecutor()
        else:
            logger.info(f"Creating command executor for {system} "
                       f"(using LinuxCommandExecutor)")
            return LinuxCommandExecutor()


@log_execution_time
def run_code_block(console: Console, code_blocks: List[str], idx: int) -> None:
    """
    Выполняет указанный блок кода и выводит результат.
    
    Args:
        console: Rich консоль для вывода
        code_blocks: Список блоков кода
        idx: Индекс выполняемого блока (начинается с 1)
    """
    logger.info(f"Starting code block #{idx}")
    
    if not _is_valid_block_index(idx, len(code_blocks)):
        _handle_invalid_block_index(console, idx, len(code_blocks))
        return
    
    code = code_blocks[idx - 1]
    logger.debug(f"Block #{idx} content: {code[:100]}...")
    
    _display_block_header(console, idx, code)
    
    try:
        _execute_code_block(console, idx, code)
    except Exception as e:
        _handle_execution_error(console, idx, e)


def _is_valid_block_index(idx: int, total_blocks: int) -> bool:
    """Проверяет корректность индекса блока."""
    return 1 <= idx <= total_blocks


def _handle_invalid_block_index(console: Console, idx: int, total_blocks: int) -> None:
    """Обрабатывает некорректный индекс блока."""
    logger.warning(f"Invalid block index: {idx}. Total blocks: {total_blocks}")
    console.print(
        t("[yellow]Block #{idx} does not exist. Available blocks: 1 to {total}.[/yellow]")
        .format(idx=idx, total=total_blocks)
    )


def _display_block_header(console: Console, idx: int, code: str) -> None:
    """Отображает заголовок и содержимое блока."""
    console.print(t("[dim]>>> Running block #{idx}:[/dim]").format(idx=idx))
    console.print(code)


def _execute_code_block(console: Console, idx: int, code: str) -> None:
    """Выполняет блок кода и отображает результат."""
    executor = CommandExecutorFactory.create_executor()
    
    logger.debug("Starting code block execution...")
    console.print(t("[dim]>>> Result:[/dim]"))
    
    result = executor.execute(code)
    
    _display_execution_result(console, idx, result)


def _display_execution_result(console: Console, idx: int, 
                            result: subprocess.CompletedProcess) -> None:
    """Отображает результат выполнения блока кода."""
    exit_code = result.returncode
    logger.info(f"Block #{idx} finished with exit code {exit_code}")
    console.print(t("[dim]>>> Exit code: {code}[/dim]").format(code=exit_code))
    
    # Показываем дополнительные ошибки если есть
    if _has_additional_errors(result):
        logger.debug(f"Additional stderr ({len(result.stderr)} chars)")
        console.print(t("[yellow]>>> Error:[/yellow]") + "\n" + result.stderr)


def _has_additional_errors(result: subprocess.CompletedProcess) -> bool:
    """Проверяет наличие дополнительных ошибок в stderr."""
    return (result.stderr and 
            not any("Error:" in line for line in result.stderr.split('\n')))


def _handle_execution_error(console: Console, idx: int, error: Exception) -> None:
    """Обрабатывает ошибки выполнения блока кода."""
    logger.error(f"Execution error in block #{idx}: {error}", exc_info=True)
    console.print(
        t("[dim]Script execution error: {error}[/dim]").format(error=error)
    )
