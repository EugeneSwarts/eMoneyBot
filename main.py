# =============================================
# Стандартные библиотеки Python
# =============================================
import asyncio
import logging
from datetime import datetime

# =============================================
# Сторонние библиотеки
# =============================================
from aiogram import types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pytz import timezone

# =============================================
# Локальные модули
# =============================================
from config import (
    LOG_FORMAT, LOG_DATE_FORMAT, LOG_LEVEL,
    LOG_USER_ACTION, bot, dp
)

from database import (
    add_user,
    create_question,
    create_review,
    get_user,
    get_user_questions,
    get_user_reviews,
    init_db
)

from keyboards import (
    get_back_keyboard,
    get_filter_type_keyboard,
    get_history_type_keyboard,
    get_main_keyboard,
    get_pagination_keyboard,
    get_review_options_keyboard,
    get_sort_type_keyboard,
    get_star_rating_keyboard
)

from messages import (
    BANNED_USER_ERROR,
    BUTTON_BACK,
    ERROR_TEXT,
    GREETING_DAY,
    GREETING_EVENING,
    GREETING_MORNING,
    GREETING_NIGHT,
    HISTORY_CHOOSE_FILTER_TEXT,
    HISTORY_CHOOSE_SORT_TEXT,
    HISTORY_CHOOSE_TYPE_TEXT,
    HISTORY_NO_QUESTIONS_TEXT,
    HISTORY_NO_REVIEWS_TEXT,
    HISTORY_QUESTIONS_HEADER,
    HISTORY_REVIEWS_HEADER,
    HISTORY_TYPE_NAMES,
    MAIN_MENU_TEXT,
    QUESTION_START_TEXT,
    REVIEW_START_TEXT,
    SUCCESS_QUESTION_TEXT,
    SUCCESS_RATING_TEXT,
    SUCCESS_REVIEW_TEXT,
    get_review_rating_text
)

from utils import (
    check_review_limit,
    check_user_ban,
    delete_last_messages,
    format_question,
    format_review,
    handle_text_message,
    safe_edit_message,
    split_items_into_pages
)

# =============================================
# Настройка системы логирования
# =============================================
# Устанавливаем базовый формат логов с временными метками
logging.basicConfig(
    level=LOG_LEVEL,
    format=LOG_FORMAT,
    datefmt=LOG_DATE_FORMAT
)

# Отключаем избыточные логи от сторонних библиотек
logging.getLogger('aiogram').setLevel(logging.WARNING)
logging.getLogger('aiohttp').setLevel(logging.WARNING)

# Создаем отдельный логгер для нашего бота
logger = logging.getLogger('bot')


# Словарь для хранения временных данных о рейтинге
user_ratings = {}

# Добавляем состояния для FSM
class ReviewStates(StatesGroup):
    """Состояния для процесса создания отзыва"""
    waiting_for_review_text = State()

class QuestionStates(StatesGroup):
    """Состояния для процесса создания вопроса"""
    waiting_for_question_text = State()

class HistoryStates(StatesGroup):
    """Состояния для просмотра истории"""
    waiting_for_history_type = State()
    waiting_for_filter_type = State()
    waiting_for_sort_type = State()

# =============================================
# Обработчик команды /start
# =============================================
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    """
    Обработчик команды /start.
    Проверяет существование пользователя, при необходимости регистрирует нового,
    и отправляет приветственное сообщение.
    
    Args:
        message (types.Message): Объект сообщения от пользователя
    """
    # Очищаем последние сообщения в чате
    await delete_last_messages(message.chat.id, message.message_id)

    # Проверяем существование пользователя и регистрируем если его нет
    user = await get_user(message.from_user.id)
    if not user:
        await add_user(message.from_user.id, message.from_user.username)
        logger.info(f"Новый пользователь: {message.from_user.id} (@{message.from_user.username})")
    
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
    
    # Отправляем приветственное сообщение с клавиатурой
    await message.answer(
        welcome_text,
        reply_markup=get_main_keyboard()
    )

# =============================================
# Обработчик нажатий на кнопки
# =============================================
@dp.callback_query()
async def process_callback(callback: types.CallbackQuery, state: FSMContext):
    """
    Обработчик нажатий на инлайн кнопки.
    Обрабатывает различные действия пользователя через кнопки меню.
    
    Args:
        callback (types.CallbackQuery): Объект callback-запроса от кнопки
        state (FSMContext): Контекст состояния FSM
    """
    user_id = callback.from_user.id
    username = callback.from_user.username or callback.from_user.first_name
    
    # Проверяем блокировку пользователя только для создания отзывов и вопросов
    if callback.data in ["leave_review", "ask_question"]:
        if await check_user_ban(user_id):
            await safe_edit_message(
                callback.message,
                BANNED_USER_ERROR,
                reply_markup=get_main_keyboard()
            )
            return

    # Логируем действие пользователя
    logger.info(LOG_USER_ACTION.format(user_id=user_id, callback_data=callback.data))
    
    # Создаем клавиатуру с кнопкой "Назад"
    back_keyboard = get_back_keyboard()
    
    # Обрабатываем различные типы действий
    if callback.data == "leave_review":
        # Проверяем, может ли пользователь оставить отзыв сегодня
        if not await check_review_limit(user_id, callback.message, back_keyboard):
            return
            
        # Пользователь хочет оставить отзыв
        await safe_edit_message(
            callback.message,
            REVIEW_START_TEXT,
            reply_markup=get_star_rating_keyboard()
        )
    elif callback.data.startswith("rating_"):
        # Проверяем, может ли пользователь оставить отзыв сегодня
        if not await check_review_limit(user_id, callback.message, back_keyboard):
            return
            
        # Пользователь выбрал оценку
        rating = int(callback.data.split("_")[1])
        user_ratings[user_id] = rating  # Сохраняем рейтинг пользователя
        await state.set_state(ReviewStates.waiting_for_review_text)
        await safe_edit_message(
            callback.message,
            get_review_rating_text(rating),
            reply_markup=get_review_options_keyboard()
        )
    elif callback.data == "skip_review_text":
        # Проверяем, может ли пользователь оставить отзыв сегодня
        if not await check_review_limit(user_id, callback.message, back_keyboard):
            return
            
        # Пользователь решил не писать отзыв
        rating = user_ratings.get(user_id)
        if rating:
            await create_review(user_id, username, rating)
            await state.clear()
            await safe_edit_message(
                callback.message,
                SUCCESS_RATING_TEXT,
                reply_markup=get_main_keyboard()
            )
            del user_ratings[user_id]
    elif callback.data == "ask_question":
        # Пользователь хочет задать вопрос
        await state.set_state(QuestionStates.waiting_for_question_text)
        await safe_edit_message(
            callback.message,
            QUESTION_START_TEXT,
            reply_markup=back_keyboard
        )
    elif callback.data == "my_reviews":
        # Пользователь хочет посмотреть историю
        await state.set_state(HistoryStates.waiting_for_history_type)
        await safe_edit_message(
            callback.message,
            HISTORY_CHOOSE_TYPE_TEXT,
            reply_markup=get_history_type_keyboard()
        )
    elif callback.data == "back_to_history":
        # Возвращаемся к выбору типа истории
        await state.set_state(HistoryStates.waiting_for_history_type)
        await safe_edit_message(
            callback.message,
            HISTORY_CHOOSE_TYPE_TEXT,
            reply_markup=get_history_type_keyboard()
        )
    elif callback.data.startswith("history_"):
        # Пользователь выбрал тип истории
        history_type = callback.data.split("_")[1]  # 'reviews' или 'questions'
        await state.set_state(HistoryStates.waiting_for_filter_type)
        await safe_edit_message(
            callback.message,
            HISTORY_CHOOSE_FILTER_TEXT.format(history_type=HISTORY_TYPE_NAMES[history_type]),
            reply_markup=await get_filter_type_keyboard(history_type, user_id)
        )
    elif callback.data.startswith("filter_"):
        # Пользователь выбрал фильтр
        _, filter_type, history_type = callback.data.split("_")
        await state.set_state(HistoryStates.waiting_for_sort_type)
        await safe_edit_message(
            callback.message,
            HISTORY_CHOOSE_SORT_TEXT.format(history_type=HISTORY_TYPE_NAMES[history_type]),
            reply_markup=get_sort_type_keyboard(history_type, filter_type)
        )
    elif callback.data.startswith("sort_"):
        # Пользователь выбрал сортировку
        _, sort_type, history_type, filter_type = callback.data.split("_")
        user_id = callback.from_user.id
        
        # Получаем данные в зависимости от выбранных параметров
        if history_type == "reviews":
            items = await get_user_reviews(
                user_id,
                with_responses_only=(filter_type == "responses"),
                sort_by_date=(sort_type == "new")
            )
            if not items:
                text = HISTORY_NO_REVIEWS_TEXT
                keyboard = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text=BUTTON_BACK, callback_data="back_to_history")]
                ])
            else:
                # Разбиваем на страницы
                pages = split_items_into_pages(items, format_review)
                current_page = pages[0]
                text = HISTORY_REVIEWS_HEADER + "".join(current_page)
                
                # Создаем клавиатуру с пагинацией
                keyboard = get_pagination_keyboard(
                    page_number=1,
                    total_pages=len(pages),
                    history_type=history_type,
                    filter_type=filter_type,
                    sort_type=sort_type
                )
        else:  # questions
            items = await get_user_questions(
                user_id,
                with_responses_only=(filter_type == "responses"),
                sort_by_date=(sort_type == "new")
            )
            if not items:
                text = HISTORY_NO_QUESTIONS_TEXT
                keyboard = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text=BUTTON_BACK, callback_data="back_to_history")]
                ])
            else:
                # Разбиваем на страницы
                pages = split_items_into_pages(items, format_question)
                current_page = pages[0]
                text = HISTORY_QUESTIONS_HEADER + "".join(current_page)
                
                # Создаем клавиатуру с пагинацией
                keyboard = get_pagination_keyboard(
                    page_number=1,
                    total_pages=len(pages),
                    history_type=history_type,
                    filter_type=filter_type,
                    sort_type=sort_type
                )
        
        await safe_edit_message(
            callback.message,
            text,
            reply_markup=keyboard
        )
    elif callback.data.startswith("page_"):
        # Обработка переключения страниц
        _, page_number, history_type, filter_type, sort_type = callback.data.split("_")
        page_number = int(page_number)
        user_id = callback.from_user.id
        
        # Получаем данные в зависимости от выбранных параметров
        if history_type == "reviews":
            items = await get_user_reviews(
                user_id,
                with_responses_only=(filter_type == "responses"),
                sort_by_date=(sort_type == "new")
            )
            pages = split_items_into_pages(items, format_review)
            text = HISTORY_REVIEWS_HEADER + "".join(pages[page_number-1])
        else:  # questions
            items = await get_user_questions(
                user_id,
                with_responses_only=(filter_type == "responses"),
                sort_by_date=(sort_type == "new")
            )
            pages = split_items_into_pages(items, format_question)
            text = HISTORY_QUESTIONS_HEADER + "".join(pages[page_number-1])
        
        # Создаем клавиатуру с пагинацией
        keyboard = get_pagination_keyboard(
            page_number=page_number,
            total_pages=len(pages),
            history_type=history_type,
            filter_type=filter_type,
            sort_type=sort_type
        )
        
        await safe_edit_message(
            callback.message,
            text,
            reply_markup=keyboard
        )
    elif callback.data.startswith("back_to_filter_"):
        # Возвращаемся к выбору фильтра
        history_type = callback.data.split("_")[-1]
        await state.set_state(HistoryStates.waiting_for_filter_type)
        await safe_edit_message(
            callback.message,
            HISTORY_CHOOSE_FILTER_TEXT.format(history_type=HISTORY_TYPE_NAMES[history_type]),
            reply_markup=await get_filter_type_keyboard(history_type, user_id)
        )
    elif callback.data == "back_to_main":
        # Возвращаемся в главное меню
        await state.clear()
        if user_id in user_ratings:
            del user_ratings[user_id]
        tyumen_tz = timezone('Asia/Yekaterinburg')
        current_hour = datetime.now(tyumen_tz).hour
        
        greeting = (
            GREETING_NIGHT if 0 <= current_hour < 6 
            else GREETING_MORNING if 6 <= current_hour < 12
            else GREETING_DAY if 12 <= current_hour < 18
            else GREETING_EVENING
        )
        
        welcome_text = f"{greeting}\n\n{MAIN_MENU_TEXT}"
        
        await safe_edit_message(
            callback.message,
            welcome_text,
            reply_markup=get_main_keyboard()
        )

# =============================================
# Обработчики текстовых сообщений
# =============================================
@dp.message(ReviewStates.waiting_for_review_text)
async def process_review_text(message: types.Message, state: FSMContext):
    """
    Обработчик текста отзыва.
    """
    await handle_text_message(
        message=message,
        state=state,
        create_func=create_review,
        success_text=SUCCESS_REVIEW_TEXT,
        error_text=ERROR_TEXT,
        user_ratings=user_ratings
    )

@dp.message(QuestionStates.waiting_for_question_text)
async def process_question_text(message: types.Message, state: FSMContext):
    """
    Обработчик текста вопроса.
    """
    await handle_text_message(
        message=message,
        state=state,
        create_func=create_question,
        success_text=SUCCESS_QUESTION_TEXT,
        error_text=ERROR_TEXT
    )

# =============================================
# Основная функция запуска бота
# =============================================
async def main():
    """
    Основная функция инициализации и запуска бота.
    Выполняет начальную настройку и запускает бота.
    """
    # Инициализируем базу данных
    await init_db()
    logger.info("База данных успешно инициализирована")
    
    # Запускаем бота
    logger.info("Бот запущен и готов к работе")
    await dp.start_polling(bot)

# =============================================
# Точка входа в программу
# =============================================
if __name__ == "__main__":
    try:
        # Запускаем бота
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        # Корректное завершение работы при нажатии Ctrl+C
        logger.info("Бот остановлен")
    except Exception as e:
        # Логируем любые непредвиденные ошибки
        logger.error(f"Произошла ошибка: {e}", exc_info=True) 