#!/usr/bin/env python3
"""
Модуль для сбора и форматирования информации о системе.

ОСОБЕННОСТИ:
- Быстрый сбор системной информации без медленных subprocess вызовов
- Поддержка множественных форматов вывода (текст, JSON, словарь)
- Локализация сообщений через систему i18n
- Обработка ошибок с graceful degradation
- Расширяемая архитектура для добавления новых типов информации
- Кэширование результатов для повышения производительности
"""

import os
import platform
import socket
import json
from datetime import datetime
from typing import Dict, Any, Optional, List
from pathlib import Path
import getpass

# Импорт системы интернационализации
from aiebash.i18n import t


class SystemInfoError(Exception):
    """Исключение для ошибок сбора системной информации."""
    pass


class ShellDetectionError(SystemInfoError):
    """Ошибка определения shell."""
    pass


class NetworkInfoError(SystemInfoError):
    """Ошибка получения сетевой информации."""
    pass

class ShellDetector:
    """
    Класс для определения типа и версии командной оболочки.
    
    Выполняет быстрое определение без медленных subprocess вызовов,
    используя анализ переменных окружения и путей к исполняемым файлам.
    """
    
    # Карта известных shell'ов
    SHELL_MAPPING = {
        'cmd.exe': ('cmd', t('Windows Command Line')),
        'powershell.exe': ('powershell', t('Windows PowerShell')),
        'pwsh.exe': ('pwsh', t('PowerShell Core')),
        'pwsh': ('pwsh', t('PowerShell Core')),
        'bash.exe': ('bash', t('Bash shell')),
        'bash': ('bash', t('Bash shell')),
        'zsh': ('zsh', t('Z shell')),
        'fish': ('fish', t('Fish shell')),
        'csh': ('csh', t('C shell')),
        'tcsh': ('tcsh', t('TCSH shell')),
        'ksh': ('ksh', t('Korn shell')),
        'dash': ('dash', t('Debian Almquist shell'))
    }
    
    def __init__(self):
        self._shell_executable = None
        self._shell_name = None
        self._shell_version = None
        self._detected = False
    
    def _detect_shell(self) -> None:
        """
        Определяет текущий shell и его характеристики.
        
        Raises:
            ShellDetectionError: При критических ошибках определения shell
        """
        if self._detected:
            return
        
        try:
            # Поиск shell в переменных окружения по приоритету
            shell_vars = ['SHELL', 'COMSPEC', 'TERMINAL', 'PSModulePath']
            
            self._shell_executable = ''
            for var in shell_vars:
                value = os.environ.get(var, '')
                if value and (os.path.exists(value) or var == 'PSModulePath'):
                    if var == 'PSModulePath':
                        # PowerShell определяется по наличию PSModulePath
                        self._shell_executable = 'powershell'
                    else:
                        self._shell_executable = value
                    break
            
            if not self._shell_executable:
                self._shell_executable = t('unknown')
                self._shell_name = t('unknown')
                self._shell_version = t('unknown')
            else:
                self._analyze_shell()
            
            self._detected = True
        
        except Exception as e:
            raise ShellDetectionError(f"Failed to detect shell: {e}")
    
    def _analyze_shell(self) -> None:
        """Анализирует тип и версию shell на основе пути к исполняемому файлу."""
        shell_basename = os.path.basename(self._shell_executable).lower()
        
        # Поиск в карте известных shell'ов
        for shell_pattern, (name, version) in self.SHELL_MAPPING.items():
            if shell_pattern.lower() in shell_basename:
                self._shell_name = name
                self._shell_version = version
                return
        
        # Если shell не найден в карте
        self._shell_name = shell_basename or t('unknown')
        self._shell_version = t('unknown shell type')
    
    def get_shell_executable(self) -> str:
        """Возвращает путь к исполняемому файлу shell."""
        self._detect_shell()
        return self._shell_executable
    
    def get_shell_name(self) -> str:
        """Возвращает имя shell."""
        self._detect_shell()
        return self._shell_name
    
    def get_shell_version(self) -> str:
        """Возвращает описание версии shell."""
        self._detect_shell()
        return self._shell_version
    
    def get_shell_info(self) -> Dict[str, str]:
        """Возвращает полную информацию о shell в виде словаря."""
        self._detect_shell()
        return {
            'executable': self._shell_executable,
            'name': self._shell_name,
            'version': self._shell_version
        }


class NetworkInfoCollector:
    """
    Класс для сбора сетевой информации системы.
    
    Выполняет безопасный сбор информации с обработкой ошибок
    и fallback значениями при недоступности сетевых ресурсов.
    """
    
    def __init__(self):
        self._hostname = None
        self._local_ip = None
        self._collected = False
    
    def _collect_network_info(self) -> None:
        """Собирает сетевую информацию с обработкой ошибок."""
        if self._collected:
            return
        
        # Получение имени хоста
        try:
            self._hostname = socket.gethostname()
        except Exception as e:
            self._hostname = t('unavailable (error: {error})').format(error=str(e))
        
        # Получение локального IP
        try:
            if self._hostname and self._hostname != t('unavailable (error: {error})').split('(')[0].strip():
                self._local_ip = socket.gethostbyname(self._hostname)
            else:
                raise NetworkInfoError("Hostname unavailable")
        except Exception as e:
            self._local_ip = t('unavailable (error: {error})').format(error=str(e))
        
        self._collected = True
    
    def get_hostname(self) -> str:
        """Возвращает имя хоста системы."""
        self._collect_network_info()
        return self._hostname
    
    def get_local_ip(self) -> str:
        """Возвращает локальный IP адрес."""
        self._collect_network_info()
        return self._local_ip
    
    def get_network_info(self) -> Dict[str, str]:
        """Возвращает полную сетевую информацию в виде словаря."""
        self._collect_network_info()
        return {
            'hostname': self._hostname,
            'local_ip': self._local_ip
        }

class SystemInfoCollector:
    """
    Главный класс для сбора и форматирования системной информации.
    
    Предоставляет различные форматы вывода информации о системе:
    - Текстовый формат для пользователей
    - JSON формат для программного использования
    - Словарь для интеграции с другими модулями
    
    Поддерживает кэширование для повышения производительности
    и локализацию всех сообщений.
    """
    
    def __init__(self, use_cache: bool = True):
        """
        Инициализирует коллектор системной информации.
        
        Args:
            use_cache: Использовать кэширование результатов
        """
        self.use_cache = use_cache
        self._shell_detector = ShellDetector()
        self._network_collector = NetworkInfoCollector()
        
        # Кэш для системной информации
        self._cached_info = None
        self._cache_timestamp = None
        self._cache_ttl = 60  # Время жизни кэша в секундах
    
    def _is_cache_valid(self) -> bool:
        """Проверяет валидность кэша."""
        if not self.use_cache or self._cached_info is None:
            return False
        
        if self._cache_timestamp is None:
            return False
        
        current_time = datetime.now()
        cache_age = (current_time - self._cache_timestamp).total_seconds()
        return cache_age < self._cache_ttl
    
    def _collect_basic_system_info(self) -> Dict[str, Any]:
        """Собирает базовую информацию о системе."""
        try:
            # Информация об операционной системе
            os_info = {
                'system': platform.system(),
                'release': platform.release(),
                'version': platform.version(),
                'architecture': platform.machine(),
                'processor': platform.processor() or t('unknown')
            }
            
            # Информация о пользователе
            try:
                username = getpass.getuser()
            except Exception:
                username = os.environ.get('USER') or os.environ.get('USERNAME') or t('unknown')
            
            user_info = {
                'username': username,
                'home_directory': os.path.expanduser("~"),
                'current_directory': os.getcwd()
            }
            
            # Информация о Python
            python_info = {
                'version': platform.python_version(),
                'implementation': platform.python_implementation(),
                'compiler': platform.python_compiler()
            }
            
            # Временная информация
            current_time = datetime.now()
            time_info = {
                'current_time': current_time.strftime("%Y-%m-%d %H:%M:%S"),
                'timezone': current_time.astimezone().tzinfo.tzname(current_time),
                'timestamp': current_time.timestamp()
            }
            
            return {
                'os': os_info,
                'user': user_info,
                'python': python_info,
                'time': time_info
            }
        
        except Exception as e:
            raise SystemInfoError(f"Failed to collect basic system info: {e}")
    
    def get_system_info_dict(self) -> Dict[str, Any]:
        """
        Возвращает полную информацию о системе в виде словаря.
        
        Returns:
            Dict[str, Any]: Структурированная информация о системе
        
        Raises:
            SystemInfoError: При критических ошибках сбора информации
        """
        # Проверяем кэш
        if self._is_cache_valid():
            return self._cached_info.copy()
        
        try:
            # Собираем базовую информацию
            system_info = self._collect_basic_system_info()
            
            # Добавляем информацию о shell
            system_info['shell'] = self._shell_detector.get_shell_info()
            
            # Добавляем сетевую информацию
            system_info['network'] = self._network_collector.get_network_info()
            
            # Обновляем кэш
            if self.use_cache:
                self._cached_info = system_info.copy()
                self._cache_timestamp = datetime.now()
            
            return system_info
        
        except Exception as e:
            raise SystemInfoError(f"Failed to collect system information: {e}")
    
    def get_system_info_text(self, language: str = 'auto') -> str:
        """
        Возвращает информацию о системе в виде форматированного текста.
        
        Args:
            language: Язык для локализации ('auto', 'ru', 'en')
        
        Returns:
            str: Форматированная текстовая информация о системе
        """
        try:
            info = self.get_system_info_dict()
            
            # Формируем локализованный текст
            lines = []
            lines.append(t("System Information:"))
            lines.append("="*50)
            
            # Информация об ОС
            os_info = info['os']
            lines.append(f"- {t('Operating System')}: {os_info['system']} {os_info['release']} ({os_info['version']})")
            lines.append(f"- {t('Architecture')}: {os_info['architecture']}")
            if os_info['processor'] and os_info['processor'] != t('unknown'):
                lines.append(f"- {t('Processor')}: {os_info['processor']}")
            
            # Информация о пользователе
            user_info = info['user']
            lines.append(f"- {t('User')}: {user_info['username']}")
            lines.append(f"- {t('Home Directory')}: {user_info['home_directory']}")
            lines.append(f"- {t('Current Directory')}: {user_info['current_directory']}")
            
            # Сетевая информация
            network_info = info['network']
            lines.append(f"- {t('Hostname')}: {network_info['hostname']}")
            lines.append(f"- {t('Local IP Address')}: {network_info['local_ip']}")
            
            # Информация о Python
            python_info = info['python']
            lines.append(f"- {t('Python Version')}: {python_info['version']} ({python_info['implementation']})")
            
            # Временная информация
            time_info = info['time']
            lines.append(f"- {t('Current Time')}: {time_info['current_time']}")
            if time_info.get('timezone'):
                lines.append(f"- {t('Timezone')}: {time_info['timezone']}")
            
            # Информация о shell
            shell_info = info['shell']
            lines.append(f"- {t('Shell')}: {shell_info['name']}")
            lines.append(f"- {t('Shell Executable')}: {shell_info['executable']}")
            lines.append(f"- {t('Shell Type')}: {shell_info['version']}")
            
            return "\n".join(lines)
        
        except Exception as e:
            # Fallback к базовой информации при ошибках
            return t("System information unavailable due to error: {error}").format(error=str(e))
    
    def get_system_info_json(self, indent: Optional[int] = 2) -> str:
        """
        Возвращает информацию о системе в формате JSON.
        
        Args:
            indent: Отступы для форматирования JSON (None для компактного формата)
        
        Returns:
            str: JSON строка с информацией о системе
        """
        try:
            info = self.get_system_info_dict()
            return json.dumps(info, indent=indent, ensure_ascii=False, default=str)
        except Exception as e:
            error_info = {
                "error": str(e),
                "message": t("Failed to collect system information")
            }
            return json.dumps(error_info, indent=indent, ensure_ascii=False)
    
    def clear_cache(self) -> None:
        """Очищает кэш системной информации."""
        self._cached_info = None
        self._cache_timestamp = None
    
    def get_cache_info(self) -> Dict[str, Any]:
        """Возвращает информацию о состоянии кэша."""
        return {
            'cache_enabled': self.use_cache,
            'cache_valid': self._is_cache_valid(),
            'cache_timestamp': self._cache_timestamp.isoformat() if self._cache_timestamp else None,
            'cache_ttl': self._cache_ttl
        }


# Глобальный экземпляр для удобства использования
_system_info_collector = SystemInfoCollector()


def get_system_info_text() -> str:
    """
    Функция обратной совместимости для получения системной информации в текстовом формате.
    
    Returns:
        str: Форматированная текстовая информация о системе
    """
    return _system_info_collector.get_system_info_text()


def get_system_info_dict() -> Dict[str, Any]:
    """
    Возвращает системную информацию в виде структурированного словаря.
    
    Returns:
        Dict[str, Any]: Структурированная информация о системе
    """
    return _system_info_collector.get_system_info_dict()


def get_system_info_json(indent: Optional[int] = 2) -> str:
    """
    Возвращает системную информацию в формате JSON.
    
    Args:
        indent: Отступы для форматирования JSON
    
    Returns:
        str: JSON строка с информацией о системе
    """
    return _system_info_collector.get_system_info_json(indent=indent)


def create_system_report(output_format: str = 'text', **kwargs) -> str:
    """
    Создает отчет о системе в указанном формате.
    
    Args:
        output_format: Формат вывода ('text', 'json', 'dict')
        **kwargs: Дополнительные параметры для форматирования
    
    Returns:
        str: Отчет о системе в указанном формате
    
    Raises:
        ValueError: При неподдерживаемом формате вывода
    """
    collector = SystemInfoCollector()
    
    if output_format.lower() == 'text':
        return collector.get_system_info_text()
    elif output_format.lower() == 'json':
        indent = kwargs.get('indent', 2)
        return collector.get_system_info_json(indent=indent)
    elif output_format.lower() == 'dict':
        return str(collector.get_system_info_dict())
    else:
        raise ValueError(t("Unsupported output format: {format}").format(format=output_format))


def get_shell_info() -> Dict[str, str]:
    """
    Быстрое получение информации только о shell.
    
    Returns:
        Dict[str, str]: Информация о командной оболочке
    """
    detector = ShellDetector()
    return detector.get_shell_info()


def get_network_info() -> Dict[str, str]:
    """
    Быстрое получение только сетевой информации.
    
    Returns:
        Dict[str, str]: Сетевая информация системы
    """
    collector = NetworkInfoCollector()
    return collector.get_network_info()


def benchmark_info_collection() -> Dict[str, float]:
    """
    Бенчмарк производительности сбора системной информации.
    
    Returns:
        Dict[str, float]: Времена выполнения различных операций в секундах
    """
    import time
    
    results = {}
    
    # Тест полного сбора информации
    start_time = time.perf_counter()
    collector = SystemInfoCollector(use_cache=False)
    collector.get_system_info_dict()
    results['full_collection'] = time.perf_counter() - start_time
    
    # Тест сбора с кэшем
    start_time = time.perf_counter()
    collector_cached = SystemInfoCollector(use_cache=True)
    collector_cached.get_system_info_dict()
    collector_cached.get_system_info_dict()  # Второй вызов из кэша
    results['cached_collection'] = time.perf_counter() - start_time
    
    # Тест только shell информации
    start_time = time.perf_counter()
    get_shell_info()
    results['shell_only'] = time.perf_counter() - start_time
    
    # Тест только сетевой информации
    start_time = time.perf_counter()
    get_network_info()
    results['network_only'] = time.perf_counter() - start_time
    
    return results


if __name__ == "__main__":
    # Демонстрация возможностей модуля
    print("=== AI-eBash System Information Module ===")
    print()
    
    # Текстовый формат
    print("1. Text format:")
    print(get_system_info_text())
    print()
    
    # JSON формат
    print("2. JSON format:")
    print(get_system_info_json())
    print()
    
    # Только shell информация
    print("3. Shell information only:")
    shell_info = get_shell_info()
    for key, value in shell_info.items():
        print(f"   {key}: {value}")
    print()
    
    # Только сетевая информация
    print("4. Network information only:")
    network_info = get_network_info()
    for key, value in network_info.items():
        print(f"   {key}: {value}")
    print()
    
    # Бенчмарк производительности
    print("5. Performance benchmark:")
    bench_results = benchmark_info_collection()
    for operation, duration in bench_results.items():
        print(f"   {operation}: {duration:.4f}s")
    print()
    
    print("✅ System information module test completed!")
