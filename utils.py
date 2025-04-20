import logging
from aiogram.types import InlineKeyboardMarkup, Message
from aiogram.exceptions import TelegramBadRequest
from datetime import datetime
from config import (
    LOG_MESSAGE_DELETE_ERROR, LOG_MESSAGE_EDIT_ERROR, LOG_DB_ERROR,
    bot  # Импортируем бота из config.py
)
from database import get_user, can_leave_review_today
from keyboards import get_main_keyboard

async def delete_last_messages(chat_id: int, message_id: int, count: int = 5):
    """
    Удаляет последние сообщения в чате.
    
    Args:
        chat_id (int): ID чата
        message_id (int): ID последнего сообщения
        count (int): Количество сообщений для удаления
    """
    error_count = 0
    current_message_id = message_id
    while error_count < count:
        try:
            await bot.delete_message(chat_id=chat_id, message_id=current_message_id)
            current_message_id -= 1
        except Exception as e:
            logging.warning(LOG_MESSAGE_DELETE_ERROR.format(message_id=current_message_id, error=e))
            current_message_id -= 1
            error_count += 1

async def safe_edit_message(message: Message, text: str, reply_markup: InlineKeyboardMarkup = None) -> None:
    """
    Безопасно редактирует сообщение с обработкой ошибок TelegramBadRequest.
    
    Args:
        message (Message): Сообщение для редактирования
        text (str): Новый текст сообщения
        reply_markup (InlineKeyboardMarkup, optional): Новая клавиатура
    """
    try:
        await message.edit_text(text, reply_markup=reply_markup)
    except TelegramBadRequest as e:
        if "message is not modified" not in str(e):
            # Логируем только если это не ошибка "сообщение не изменено"
            logging.warning(LOG_MESSAGE_EDIT_ERROR.format(error=e))

async def check_user_ban(user_id: int) -> bool:
    """
    Проверяет, заблокирован ли пользователь.
    
    Args:
        user_id (int): ID пользователя
        
    Returns:
        bool: True если пользователь заблокирован, False если нет
    """
    user = await get_user(user_id)
    return user and user[3]  # user[3] - это поле is_banned

async def check_review_limit(user_id: int, message: Message, keyboard: InlineKeyboardMarkup) -> bool:
    """
    Проверяет, может ли пользователь оставить отзыв сегодня.
    
    Args:
        user_id (int): ID пользователя
        message (Message): Сообщение для редактирования
        keyboard (InlineKeyboardMarkup): Клавиатура для возврата
        
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
    state,
    create_func: callable,
    success_text: str,
    error_text: str,
    user_ratings: dict = None
) -> None:
    """
    Обрабатывает текстовые сообщения (отзывы и вопросы).
    
    Args:
        message (Message): Объект сообщения
        state: Контекст состояния FSM
        create_func (callable): Функция для создания записи
        success_text (str): Текст успешного создания
        error_text (str): Текст ошибки
        user_ratings (dict, optional): Словарь с рейтингами пользователей
    """
    user_id = message.from_user.id
    username = message.from_user.username or message.from_user.first_name
    
    # Удаляем предыдущие сообщения
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
        # Создаем запись
        if user_ratings:
            rating = user_ratings.get(user_id)
            if not rating:
                await message.answer(error_text)
                await state.clear()
                return
            await create_func(user_id, username, rating, message.text)
        else:
            await create_func(user_id, username, message.text)
            
        await message.answer(
            success_text,
            reply_markup=get_main_keyboard()
        )
    except Exception as e:
        logging.error(LOG_DB_ERROR.format(error=e))
        await message.answer(error_text)
    finally:
        await state.clear()
        if user_ratings:
            user_ratings.pop(user_id, None)

def format_datetime(datetime_str: str) -> str:
    """
    Форматирует строку с датой и временем.
    
    Args:
        datetime_str (str): Строка с датой и временем в формате ISO
        
    Returns:
        str: Отформатированная дата и время
    """
    return datetime.fromisoformat(datetime_str).strftime("%d.%m.%Y %H:%M")

def format_review(review: tuple) -> str:
    """
    Форматирует отзыв для отображения.
    
    Args:
        review (tuple): Данные отзыва из базы данных
        
    Returns:
        str: Отформатированный текст отзыва
    """
    review_id, user_id, username, rating, review_text, admin_response, created_at = review
    
    formatted_text = f"""
📅 Дата: {format_datetime(created_at)}
⭐ Оценка: {'⭐' * rating}
📝 Отзыв: {review_text}
"""
    if admin_response:
        formatted_text += f"💬 Ответ администратора: {admin_response}\n\n"
    
    return formatted_text

def format_question(question: tuple) -> str:
    """
    Форматирует вопрос для отображения.
    
    Args:
        question (tuple): Данные вопроса из базы данных
        
    Returns:
        str: Отформатированный текст вопроса
    """
    question_id, user_id, username, question_text, admin_response, created_at = question
    
    formatted_text = f"""
📅 Дата: {format_datetime(created_at)}
❓ Вопрос: {question_text}
"""
    if admin_response:
        formatted_text += f"💬 Ответ администратора: {admin_response}\n\n"
    
    return formatted_text

def split_items_into_pages(items: list, format_func: callable) -> list:
    """
    Разделяет список элементов на страницы с учетом максимального количества символов и элементов.
    
    Args:
        items (list): Список элементов для отображения
        format_func (callable): Функция форматирования элемента
        
    Returns:
        list: Список страниц с отформатированными элементами
    """
    pages = []
    current_page = []
    current_page_length = 0
    
    for item in items:
        formatted_item = format_func(item)
        item_length = len(formatted_item)
        
        # Если текущая страница пуста или элемент помещается на текущую страницу
        if not current_page or (current_page_length + item_length <= 4000 and len(current_page) < 10):
            current_page.append(formatted_item)
            current_page_length += item_length
        else:
            # Сохраняем текущую страницу и начинаем новую
            pages.append(current_page)
            current_page = [formatted_item]
            current_page_length = item_length
    
    # Добавляем последнюю страницу, если она не пуста
    if current_page:
        pages.append(current_page)
    
    return pages 