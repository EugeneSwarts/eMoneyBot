from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from src.database import get_user, get_all_reviews, get_all_questions
from src.formatting import format_datetime
from .admin_keyboards import (
    get_admin_menu_keyboard, 
    get_admin_questions_keyboard, 
    get_admin_reviews_keyboard,
    get_admin_sort_type_keyboard,
    get_admin_pagination_keyboard,
    get_admin_history_keyboard
)
from .admin_messages import (
    ADMIN_MENU_TEXT, 
    ADMIN_REVIEWS_FILTER_TEXT,
    ADMIN_QUESTIONS_FILTER_TEXT,
    ADMIN_SORT_TEXT,
    ADMIN_HISTORY_REVIEW_TEMPLATE,
    ADMIN_HISTORY_QUESTION_TEMPLATE,
    ADMIN_HISTORY_NO_REVIEWS,
    ADMIN_HISTORY_NO_QUESTIONS,
    ADMIN_HISTORY_STATUS_WITH_ANSWER,
    ADMIN_HISTORY_STATUS_WITHOUT_ANSWER
)

class AdminHistoryStates(StatesGroup):
    """
    Класс состояний для управления историей в панели администратора.
    
    Состояния:
    - waiting_for_filter_type: Ожидание выбора типа фильтрации
    - waiting_for_sort_type: Ожидание выбора типа сортировки
    - viewing_history: Просмотр истории с пагинацией
    """
    waiting_for_filter_type = State()
    waiting_for_sort_type = State()
    viewing_history = State()

async def show_admin_menu(message, user_id: int, is_bot: bool):
    """
    Отображает главное меню администратора.
    Доступно только для пользователей с правами администратора.
    
    Уровни доступа:
    1 - Просмотр отзывов и вопросов
    2 - Ответы на отзывы и вопросы
    3 - Полный доступ (управление администраторами и блокировки)
    
    Args:
        message (types.Message | types.CallbackQuery): Объект сообщения или callback
        user_id (int): ID пользователя
        is_bot (bool): True если callback, False если обычное сообщение
        
    Returns:
        bool: True если меню показано успешно, False если нет прав администратора
    """
    # Проверяем права администратора
    user = await get_user(user_id)
    admin_level = user[2]
    
    # Получаем клавиатуру для текущего уровня доступа
    keyboard = get_admin_menu_keyboard(admin_level)

    if is_bot:
        # Если это callback, редактируем существующее сообщение
        try:
            if isinstance(message, types.CallbackQuery):
                await message.message.edit_text(ADMIN_MENU_TEXT, reply_markup=keyboard)
            else:
                await message.edit_text(ADMIN_MENU_TEXT, reply_markup=keyboard)
        except Exception as e:
            # Если возникла ошибка при редактировании, просто игнорируем её
            # Это может произойти, если сообщение уже содержит тот же текст и клавиатуру
            pass
    else:
        # Если обычное сообщение, отправляем новое
        await message.answer(ADMIN_MENU_TEXT, reply_markup=keyboard)
    
    return True

async def handle_admin_reviews(callback: types.CallbackQuery, state: FSMContext):
    """
    Обрабатывает нажатие на кнопку "Отзывы" в главном меню администратора.
    
    Args:
        callback (types.CallbackQuery): Объект callback запроса
        state (FSMContext): Контекст состояния FSM
    """
    await state.set_state(AdminHistoryStates.waiting_for_filter_type)
    await callback.message.edit_text(
        ADMIN_REVIEWS_FILTER_TEXT,
        reply_markup=get_admin_reviews_keyboard()
    )

async def handle_admin_questions(callback: types.CallbackQuery, state: FSMContext):
    """
    Обрабатывает нажатие на кнопку "Вопросы" в главном меню администратора.
    
    Args:
        callback (types.CallbackQuery): Объект callback запроса
        state (FSMContext): Контекст состояния FSM
    """
    await state.set_state(AdminHistoryStates.waiting_for_filter_type)
    await callback.message.edit_text(
        ADMIN_QUESTIONS_FILTER_TEXT,
        reply_markup=get_admin_questions_keyboard()
    )

async def show_admin_reviews(callback: types.CallbackQuery, state: FSMContext, filter_type: str):
    """
    Показывает отзывы администратору с учетом фильтрации.
    
    Args:
        callback (types.CallbackQuery): Объект callback запроса
        state (FSMContext): Контекст состояния FSM
        filter_type (str): Тип фильтрации ('all' или 'without_answers')
    """
    await state.set_state(AdminHistoryStates.waiting_for_sort_type)
    await state.update_data(filter_type=filter_type, history_type="reviews")
    await callback.message.edit_text(
        ADMIN_SORT_TEXT,
        reply_markup=get_admin_sort_type_keyboard("reviews", filter_type)
    )

async def show_admin_questions(callback: types.CallbackQuery, state: FSMContext, filter_type: str):
    """
    Показывает вопросы администратору с учетом фильтрации.
    
    Args:
        callback (types.CallbackQuery): Объект callback запроса
        state (FSMContext): Контекст состояния FSM
        filter_type (str): Тип фильтрации ('all' или 'without_answers')
    """
    await state.set_state(AdminHistoryStates.waiting_for_sort_type)
    await state.update_data(filter_type=filter_type, history_type="questions")
    await callback.message.edit_text(
        ADMIN_SORT_TEXT,
        reply_markup=get_admin_sort_type_keyboard("questions", filter_type)
    )

async def display_admin_history(callback: types.CallbackQuery, state: FSMContext, sort_type: str):
    """
    Отображает историю (отзывы или вопросы) с учетом фильтрации и сортировки.
    
    Args:
        callback (types.CallbackQuery): Объект callback запроса
        state (FSMContext): Контекст состояния FSM
        sort_type (str): Тип сортировки ('new' или 'old')
    """
    data = await state.get_data()
    filter_type = data.get("filter_type", "all")
    history_type = data.get("history_type", "reviews")
    
    # Получаем данные в зависимости от типа истории
    if history_type == "reviews":
        items = await get_all_reviews(filter_type)
        if not items:
            await callback.message.edit_text(
                ADMIN_HISTORY_NO_REVIEWS,
                reply_markup=get_admin_reviews_keyboard()
            )
            return
    else:
        items = await get_all_questions(filter_type)
        if not items:
            await callback.message.edit_text(
                ADMIN_HISTORY_NO_QUESTIONS,
                reply_markup=get_admin_questions_keyboard()
            )
            return
    
    # Сортируем элементы с учетом возможных None значений
    def sort_key(item):
        # Для отзывов используем created_at (индекс 6), для вопросов - created_at (индекс 5)
        date = item[6] if history_type == "reviews" else item[5]
        if date is None:
            return ""  # Пустая строка для сортировки None значений в конец
        return date
    
    if sort_type == "old":
        items = sorted(items, key=sort_key)
    else:
        items = sorted(items, key=sort_key, reverse=True)
    
    # Сохраняем отсортированные элементы в состоянии
    await state.update_data(items=items, current_page=0)
    await state.set_state(AdminHistoryStates.viewing_history)
    
    # Отображаем первую страницу
    await show_admin_history_page(callback, state)

async def show_admin_history_page(callback: types.CallbackQuery, state: FSMContext):
    """
    Отображает страницу истории с пагинацией.
    
    Args:
        callback (types.CallbackQuery): Объект callback запроса
        state (FSMContext): Контекст состояния FSM
    """
    data = await state.get_data()
    items = data.get("items", [])
    current_page = data.get("current_page", 0)
    history_type = data.get("history_type", "reviews")
    filter_type = data.get("filter_type", "all")

    # Проверяем права администратора
    user_data = await get_user(callback.from_user.id)
    admin_level = user_data[2]  # Получаем уровень администратора из базы данных
    
    # Разбиваем на страницы по 1 элементу
    items_per_page = 1
    total_pages = len(items)
    
    if total_pages == 0:
        if history_type == "reviews":
            await callback.message.edit_text(
                ADMIN_HISTORY_NO_REVIEWS,
                reply_markup=get_admin_reviews_keyboard()
            )
        else:
            await callback.message.edit_text(
                ADMIN_HISTORY_NO_QUESTIONS,
                reply_markup=get_admin_questions_keyboard()
            )
        return
    
    # Проверяем корректность текущей страницы
    if current_page < 0:
        current_page = 0
    elif current_page >= total_pages:
        current_page = total_pages - 1
    
    # Получаем текущий элемент
    current_item = items[current_page]
    
    # Формируем текст страницы
    if history_type == "reviews":
        status = ADMIN_HISTORY_STATUS_WITH_ANSWER if current_item[5] else ADMIN_HISTORY_STATUS_WITHOUT_ANSWER
        review_text = f"\n💭 Отзыв: {current_item[4]}" if current_item[4] else ""
        admin_response = f"\n💬 Ответ администратора: {current_item[5]}" if current_item[5] else ""
        
        text = ADMIN_HISTORY_REVIEW_TEMPLATE.format(
            review_id=current_item[0],
            username=current_item[2],
            status=status,
            date=format_datetime(current_item[6]),
            rating="⭐" * current_item[3],
            review_text=review_text,
            admin_response=admin_response
        )
    else:
        status = ADMIN_HISTORY_STATUS_WITH_ANSWER if current_item[4] else ADMIN_HISTORY_STATUS_WITHOUT_ANSWER
        admin_response = f"\n💬 Ответ администратора: {current_item[4]}" if current_item[4] else ""
        
        text = ADMIN_HISTORY_QUESTION_TEMPLATE.format(
            question_id=current_item[0],
            username=current_item[2],
            status=status,
            date=format_datetime(current_item[5]),
            question_text=current_item[3],
            admin_response=admin_response
        )
    
    # Создаем клавиатуру с пагинацией
    keyboard = get_admin_history_keyboard(
        current_page=current_page,
        total_pages=total_pages,
        history_type=history_type,
        filter_type=filter_type,
        has_admin_response=current_item[5] if history_type == "reviews" else current_item[4],
        admin_level=admin_level,
        item_id=current_item[0]
    )
    
    await callback.message.edit_text(text, reply_markup=keyboard)


