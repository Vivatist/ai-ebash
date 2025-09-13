# --- Top-level imports ---
from typing import List, Dict, Optional
from rich.console import Console
from rich.markdown import Markdown
from aiebash.formatter_text import annotate_code_blocks
from aiebash.script_executor import run_code_block
from aiebash.config_manager import config_manager
from aiebash.logger import logger


def _render_answer(console: Console, answer: str) -> List[str]:
    """Отрисовать ответ AI. При run_mode=True нумеруем bash-блоки, иначе просто показываем текст.
    Возвращает список bash-блоков (только при run_mode=True), иначе пустой список.
    """
    console.print("[bold blue]AI:[/bold blue]")
    logger.debug("Аннотирование и форматирование ответа от ИИ...")
    annotated_answer, code_blocks = annotate_code_blocks(answer)
    
    logger.debug(f"Текст ИИ в формате Markdown (с учетом аннотаций):\n{annotated_answer}")

    console.print(Markdown(annotated_answer))
    return code_blocks


def chat_loop(console: Console, llm_client, context: str, first_prompt: Optional[str]) -> None:
    """
    Запускает диалоговый режим с LLM.
    
    Args:
        console: Консоль для вывода
        llm_client: Клиент для взаимодействия с LLM
        context: Системный контекст для LLM
        first_prompt: Первый запрос пользователя (опционально)
    """
    logger.info("Запуск диалогового режима")
    messages: List[Dict[str, str]] = []
    
    if context:
        logger.debug(f"Установка системного контекста: {context[:50]}...")
        messages.append({"role": "system", "content": context})
    else:
        logger.debug("Системный контекст не задан")

    code_blocks: List[str] = []

    # Первый вопрос
    if first_prompt:
        logger.info(f"Обработка первого запроса: {first_prompt[:50]}...")
        messages.append({"role": "user", "content": first_prompt})
        
        try:
            logger.debug("Отправка первого запроса диалога")
            answer: str = llm_client.send_chat(messages)
            
            messages.append({"role": "assistant", "content": answer})
            code_blocks = _render_answer(console, answer)
            logger.info(f"Первый ответ отрендерен, найдено {len(code_blocks)} блоков кода")
        except Exception as e:
            logger.error(f"Ошибка при обработке первого запроса: {e}", exc_info=True)


    # Основной цикл
    logger.info("Запуск основного диалогового цикла")
    while True:
        try:
            # Вывод подсказки в зависимости от наличия блоков кода
            if len(code_blocks) > 0:
                logger.debug(f"Ожидание ввода пользователя (доступно {len(code_blocks)} блоков кода)")
                console.print("[dim]Введите следующий вопрос или номер блока кода для немедленного выполнения[/dim]")
            else:
                logger.debug("Ожидание ввода пользователя")
                console.print("[dim]Введите следующий вопрос[/dim]")
                
            # Ввод пользователя
            user_input: str = console.input("[bold green]Вы:[/bold green] ")
            stripped = user_input.strip()
            
            # Проверка на выход
            if stripped.lower() in ("exit", "quit", "выход"):
                logger.info("Пользователь запросил выход из диалога")
                break

            # Если введено число — попытка запуска блока
            if stripped.isdigit():
                idx = int(stripped)
                logger.debug(f"Пользователь запросил запуск блока #{idx}")
                
                if 1 <= idx <= len(code_blocks):
                    logger.info(f"Запуск блока кода #{idx}")
                    run_code_block(console, code_blocks, idx)
                else:
                    logger.warning(f"Запрошен несуществующий блок #{idx}, доступно {len(code_blocks)} блоков")
                    console.print("[yellow]Нет такого блока. Введите номер из списка или текстовый запрос.[/yellow]")
                continue  # Возвращаемся к вводу промпта

            # Обычное сообщение пользователя
            logger.info(f"Новый запрос пользователя: {user_input[:50]}...")
            messages.append({"role": "user", "content": user_input})
            
            try:
                logger.debug("Отправка запроса к LLM")
                answer = llm_client.send_chat(messages)
                
                messages.append({"role": "assistant", "content": answer})
                code_blocks = _render_answer(console, answer)
                logger.info(f"Ответ отрендерен, найдено {len(code_blocks)} блоков кода")
            except Exception as e:
                logger.error(f"Ошибка при обработке запроса: {e}", exc_info=True)
                console.print(f"[red]Ошибка при обработке запроса: {e}[/red]")

        except KeyboardInterrupt:
            logger.info("Диалог прерван пользователем (Ctrl+C)")
            console.print("\n")
            break
    
    logger.info("Диалоговый режим завершен")
