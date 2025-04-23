# =============================================
# Стандартные библиотеки Python
# =============================================
from asyncio.log import logger
from datetime import datetime
import logging
from typing import Optional, List, Callable, Dict, Any, Union

# =============================================
# Сторонние библиотеки
# =============================================
from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
import aiosqlite
from pytz import timezone

# =============================================
# Внутренние модули
# =============================================
from src.admin.admin_messages import ADMIN_HISTORY_QUESTION_TEMPLATE, ADMIN_HISTORY_REVIEW_TEMPLATE, ADMIN_HISTORY_STATUS_WITHOUT_ANSWER
from src.admin.admin_utils import show_admin_menu
from src.config import (
    DATABASE_PATH,
    LOG_MESSAGE_DELETE_ERROR,
    LOG_MESSAGE_EDIT_ERROR,
    LOG_DB_ERROR,
    bot
)
from src.database import add_user, get_questions_by_id, get_review_by_id, get_user, can_leave_review_today
from src.keyboards import get_main_keyboard
from src.messages import *
from src.formatting import format_datetime


# =============================================
# Обработчик главного меню
# =============================================
async def handle_main_menu(message: Union[types.Message, types.CallbackQuery], is_start: bool = False) -> None:
    """
    Общий обработчик для главного меню.
    Используется как для команды /start, так и для кнопки "Назад".
    
    Args:
        message (Union[types.Message, types.CallbackQuery]): Объект сообщения или callback
        is_start (bool): True если это команда /start, False если возврат в меню
    """
    # Очищаем последние сообщения только для команды start
    if is_start:
        await delete_last_messages(message.chat.id, message.message_id)
        
        # Проверяем существование пользователя и регистрируем если его нет
        user = await get_user(message.from_user.id)
        if not user:
            await add_user(message.from_user.id, message.from_user.username)
            logger.info(f"Новый пользователь: {message.from_user.id} (@{message.from_user.username})")
        
        # Проверяем права администратора
        if await check_admin_rights(message):
            return

    # Определяем текущее время суток для персонализированного приветствия
    tyumen_tz = timezone('Asia/Yekaterinburg')
    current_hour = datetime.now(tyumen_tz).hour
    
    # Выбираем подходящее приветствие в зависимости от времени суток
    greeting = (
        GREETING_NIGHT if 0 <= current_hour < 6 
        else GREETING_MORNING if 6 <= current_hour < 12
        else GREETING_DAY if 12 <= current_hour < 18
        else GREETING_EVENING
    )
    
    # Формируем текст приветственного сообщения
    welcome_text = f"{greeting}\n\n{MAIN_MENU_TEXT}"
    
    # Отправляем или редактируем сообщение в зависимости от типа вызова
    if is_start:
        await message.answer(welcome_text, reply_markup=get_main_keyboard())
    else:
        # Если это CallbackQuery, используем его message атрибут
        message_to_edit = message.message if isinstance(message, types.CallbackQuery) else message
        await safe_edit_message(message_to_edit, welcome_text, reply_markup=get_main_keyboard())

# =============================================
# Управление сообщениями в чате
# =============================================
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

# =============================================
# Проверки пользователей и прав доступа
# =============================================
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
            REVIEW_LIMIT_TEXT,
            reply_markup=keyboard
        )
        return False
    return True


async def check_admin_rights(message: Union[Message, types.CallbackQuery]) -> bool:
    """
    Проверяет права администратора пользователя и выполняет перенаправление на админ-меню при необходимости.
    
    Args:
        message (Union[Message, types.CallbackQuery]): Объект сообщения или callback query от пользователя
        
    Returns:
        bool: True если пользователь администратор, False если нет
    """
    # Определяем ID пользователя в зависимости от типа входящего сообщения
    user_id = message.chat.id if message.from_user.is_bot else message.from_user.id
    user = await get_user(user_id)
    
    if user and user[2] > 0:  # user[2] - это поле admin_rights в базе данных
        await show_admin_menu(message, user_id, message.from_user.is_bot)
        return True
    return False


async def check_user_rights(message: Union[Message, types.CallbackQuery]) -> bool:
    """
    Проверяет права пользователя и выполняет перенаправление на меню при необходимости.
    
    Args:
        message (Union[Message, types.CallbackQuery]): Объект сообщения или callback query от пользователя
        
    Returns:
        bool: True если пользователь администратор, False если нет
    """
    # Определяем ID пользователя в зависимости от типа входящего сообщения
    user_id = message.chat.id if message.from_user.is_bot else message.from_user.id
    user = await get_user(user_id)
    
    if user and user[2] < 1:  # user[2] - это поле admin_rights в базе данных
        await handle_main_menu(message, is_start=False)
        return True
    return False

# =============================================
# Обработка пользовательского ввода
# =============================================
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
            item_id = await create_func(user_id, username, rating, message.text)
        else:
            item_id = await create_func(user_id, username, message.text)
            
        # Отправляем сообщение об успехе
        await message.answer(
            success_text,
            reply_markup=get_main_keyboard()
        )
        
        # Определяем тип записи (отзыв или вопрос)
        history_type = "reviews" if user_ratings else "questions"
        
        # Получаем данные записи для уведомления
        if history_type == "reviews":
            item = await get_review_by_id(item_id)
            status = ADMIN_HISTORY_STATUS_WITHOUT_ANSWER
            item_text = f"\n\n💭 Отзыв: {item[4]}" if item[4] else ""
            
            # Формируем текст уведомления
            notification_text = ADMIN_HISTORY_REVIEW_TEMPLATE.format(
                review_id=item[0],
                username=item[2],
                status=status,
                date=format_datetime(item[6]),
                rating="⭐" * item[3],
                review_text=item_text,
                admin_response=""
            )
        else:
            item = await get_questions_by_id(item_id)
            status = ADMIN_HISTORY_STATUS_WITHOUT_ANSWER
            
            # Формируем текст уведомления
            notification_text = ADMIN_HISTORY_QUESTION_TEMPLATE.format(
                question_id=item[0],
                username=item[2],
                status=status,
                date=format_datetime(item[5]),
                question_text=f"{item[3]}",
                admin_response=""
            )
        
        # Получаем всех администраторов и отправляем им уведомления
        async with aiosqlite.connect(DATABASE_PATH) as db:
            async with db.execute('SELECT user_id FROM users WHERE admin_level > 0') as cursor:
                admins = await cursor.fetchall()
                for admin in admins:
                    try:
                        # Создаем кнопку для удаления уведомления
                        keyboard = InlineKeyboardMarkup(
                            inline_keyboard=[
                                [InlineKeyboardButton(text="✅ OK", callback_data="delete_notification")]
                            ]
                        )
                        await bot.send_message(admin[0], notification_text, reply_markup=keyboard)
                    except Exception as e:
                        logger.error(f"Ошибка при отправке уведомления администратору: {e}")
                        continue
                        
    except Exception as e:
        # Логируем ошибку и отправляем сообщение пользователю
        logging.error(LOG_DB_ERROR.format(error=e))
        await message.answer(error_text)
    finally:
        # Очищаем состояние и удаляем рейтинг пользователя
        await state.clear()
        if user_ratings:
            user_ratings.pop(user_id, None)

# =============================================
# Форматирование данных
# =============================================
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

    # Форматируем отзыв
    review_text = f"\n\n💭 Отзыв: {review_text}" if review_text else ""
    # Форматируем ответ администратора
    admin_response_text = f"\n\n💬 Ответ администратора: {admin_response}" if admin_response else ""
    
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
    admin_response_text = f"\n\n💬 Ответ администратора: {admin_response}" if admin_response else ""
    
    # Используем формат из messages.py
    return QUESTION_FORMAT.format(
        date=format_datetime(created_at),
        question_text=question_text,
        admin_response=admin_response_text
    )

# =============================================
# Пагинация и навигация
# =============================================
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