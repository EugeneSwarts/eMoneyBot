import logging
from datetime import datetime
from typing import Optional, List, Callable, Dict, Any, Union

from aiogram.types import InlineKeyboardMarkup, Message
from aiogram.exceptions import TelegramBadRequest

from src.config import (
    LOG_MESSAGE_DELETE_ERROR,
    LOG_MESSAGE_EDIT_ERROR,
    LOG_DB_ERROR,
    bot
)
from src.database import get_user, can_leave_review_today
from src.keyboards import get_main_keyboard
from src.messages import MAX_CHARS_PER_PAGE, MAX_ITEMS_PER_PAGE, QUESTION_FORMAT, REVIEW_FORMAT


async def delete_last_messages(chat_id: int, message_id: int, count: int = 5) -> None:
    """
    Удаляет последние сообщения в чате.
    Используется для очистки истории сообщений после выполнения команд.
    
    Args:
        chat_id (int): ID чата, в котором нужно удалить сообщения
        message_id (int): ID последнего сообщения, с которого начинается удаление
        count (int): Количество сообщений для удаления (по умолчанию 5)
    """
    error_count = 0
    current_message_id = message_id
    
    # Пытаемся удалить сообщения, пока не достигнем лимита ошибок
    while error_count < count:
        try:
            await bot.delete_message(chat_id=chat_id, message_id=current_message_id)
            current_message_id -= 1
        except Exception as e:
            # Логируем ошибку удаления сообщения
            logging.warning(LOG_MESSAGE_DELETE_ERROR.format(
                message_id=current_message_id,
                error=e
            ))
            current_message_id -= 1
            error_count += 1


async def safe_edit_message(
    message: Message,
    text: str,
    reply_markup: Optional[InlineKeyboardMarkup] = None
) -> None:
    """
    Безопасно редактирует сообщение с обработкой ошибок TelegramBadRequest.
    Используется для обновления сообщений без вызова исключений.
    
    Args:
        message (Message): Сообщение для редактирования
        text (str): Новый текст сообщения
        reply_markup (InlineKeyboardMarkup, optional): Новая клавиатура
    """
    try:
        await message.edit_text(text, reply_markup=reply_markup)
    except TelegramBadRequest as e:
        # Игнорируем ошибку, если сообщение не было изменено
        if "message is not modified" not in str(e):
            logging.warning(LOG_MESSAGE_EDIT_ERROR.format(error=e))


async def check_user_ban(user_id: int) -> bool:
    """
    Проверяет, заблокирован ли пользователь.
    Используется для ограничения доступа заблокированных пользователей.
    
    Args:
        user_id (int): ID пользователя для проверки
        
    Returns:
        bool: True если пользователь заблокирован, False если нет
    """
    user = await get_user(user_id)
    return user and user[3]  # user[3] - это поле is_banned в базе данных


async def check_review_limit(
    user_id: int,
    message: Message,
    keyboard: InlineKeyboardMarkup
) -> bool:
    """
    Проверяет, может ли пользователь оставить отзыв сегодня.
    Ограничивает количество отзывов от одного пользователя в день.
    
    Args:
        user_id (int): ID пользователя
        message (Message): Сообщение для редактирования
        keyboard (InlineKeyboardMarkup): Клавиатура для возврата в главное меню
        
    Returns:
        bool: True если пользователь может оставить отзыв, False если нет
    """
    if not await can_leave_review_today(user_id):
        await safe_edit_message(
            message,
            "Вы уже оставили отзыв сегодня. Попробуйте завтра.",
            reply_markup=keyboard
        )
        return False
    return True


async def handle_text_message(
    message: Message,
    state: Any,
    create_func: Callable,
    success_text: str,
    error_text: str,
    user_ratings: Optional[Dict[int, int]] = None
) -> None:
    """
    Обрабатывает текстовые сообщения (отзывы и вопросы).
    Универсальная функция для обработки пользовательского ввода.
    
    Args:
        message (Message): Объект сообщения от пользователя
        state: Контекст состояния FSM для управления состоянием диалога
        create_func (Callable): Функция для создания записи в базе данных
        success_text (str): Текст успешного создания записи
        error_text (str): Текст ошибки при создании записи
        user_ratings (Dict[int, int], optional): Словарь с рейтингами пользователей
    """
    # Получаем информацию о пользователе
    user_id = message.from_user.id
    username = message.from_user.username or message.from_user.first_name
    
    # Очищаем предыдущие сообщения
    await delete_last_messages(message.chat.id, message.message_id)
    
    # Проверяем блокировку пользователя
    if await check_user_ban(user_id):
        await message.answer(
            "Вы заблокированы и не можете оставлять отзывы или задавать вопросы.",
            reply_markup=get_main_keyboard()
        )
        await state.clear()
        return

    try:
        # Создаем запись в базе данных
        if user_ratings:
            rating = user_ratings.get(user_id)
            if not rating:
                await message.answer(error_text)
                await state.clear()
                return
            await create_func(user_id, username, rating, message.text)
        else:
            await create_func(user_id, username, message.text)
            
        # Отправляем сообщение об успехе
        await message.answer(
            success_text,
            reply_markup=get_main_keyboard()
        )
    except Exception as e:
        # Логируем ошибку и отправляем сообщение пользователю
        logging.error(LOG_DB_ERROR.format(error=e))
        await message.answer(error_text)
    finally:
        # Очищаем состояние и удаляем рейтинг пользователя
        await state.clear()
        if user_ratings:
            user_ratings.pop(user_id, None)


def format_datetime(datetime_str: str) -> str:
    """
    Форматирует строку с датой и временем.
    Преобразует ISO формат в читаемый формат даты и времени.
    
    Args:
        datetime_str (str): Строка с датой и временем в формате ISO
        
    Returns:
        str: Отформатированная дата и время в формате "дд.мм.гггг чч:мм"
    """
    return datetime.fromisoformat(datetime_str).strftime("%d.%m.%Y %H:%M")


def format_review(review: tuple) -> str:
    """
    Форматирует отзыв для отображения.
    Создает читаемое представление отзыва с эмодзи и форматированием.
    
    Args:
        review (tuple): Данные отзыва из базы данных
        
    Returns:
        str: Отформатированный текст отзыва с датой, рейтингом и текстом
    """
    review_id, user_id, username, rating, review_text, admin_response, created_at = review
    
    # Форматируем ответ администратора
    admin_response_text = f"💬 Ответ администратора: {admin_response}" if admin_response else ""
    
    # Используем формат из messages.py
    return REVIEW_FORMAT.format(
        date=format_datetime(created_at),
        rating="⭐" * rating,
        review_text=review_text,
        admin_response=admin_response_text
    )


def format_question(question: tuple) -> str:
    """
    Форматирует вопрос для отображения.
    Создает читаемое представление вопроса с эмодзи и форматированием.
    
    Args:
        question (tuple): Данные вопроса из базы данных
        
    Returns:
        str: Отформатированный текст вопроса с датой и текстом
    """
    question_id, user_id, username, question_text, admin_response, created_at = question
    
    # Форматируем ответ администратора
    admin_response_text = f"💬 Ответ администратора: {admin_response}" if admin_response else ""
    
    # Используем формат из messages.py
    return QUESTION_FORMAT.format(
        date=format_datetime(created_at),
        question_text=question_text,
        admin_response=admin_response_text
    )


def split_items_into_pages(
    items: List[Any],
    format_func: Callable[[Any], str]
) -> List[List[str]]:
    """
    Разделяет список элементов на страницы с учетом максимального количества символов и элементов.
    Используется для пагинации длинных списков отзывов или вопросов.
    
    Args:
        items (List[Any]): Список элементов для отображения
        format_func (Callable[[Any], str]): Функция форматирования элемента
        
    Returns:
        List[List[str]]: Список страниц с отформатированными элементами
    """
    pages = []
    current_page = []
    current_page_length = 0
    
    # Разбиваем элементы на страницы
    for item in items:
        formatted_item = format_func(item)
        item_length = len(formatted_item)
        
        # Проверяем, помещается ли элемент на текущую страницу
        if not current_page or (current_page_length + item_length <= MAX_CHARS_PER_PAGE and len(current_page) < MAX_ITEMS_PER_PAGE):
            current_page.append(formatted_item)
            current_page_length += item_length
        else:
            # Создаем новую страницу
            pages.append(current_page)
            current_page = [formatted_item]
            current_page_length = item_length
    
    # Добавляем последнюю страницу, если она не пуста
    if current_page:
        pages.append(current_page)
    
    return pages 