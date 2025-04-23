from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from src.database import get_questions_by_id, get_user, get_all_reviews, get_all_questions, add_review_response, add_question_response, get_review_by_id
from src.formatting import format_datetime
from src.utils import delete_last_messages
from .admin_utils import show_admin_menu
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
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

class AdminHistoryStates(StatesGroup):
    """
    Класс состояний для управления историей в панели администратора.
    
    Состояния:
    - waiting_for_filter_type: Ожидание выбора типа фильтрации
    - waiting_for_sort_type: Ожидание выбора типа сортировки
    - viewing_history: Просмотр истории с пагинацией
    - waiting_for_reply: Ожидание ответа администратора
    """
    waiting_for_filter_type = State()
    waiting_for_sort_type = State()
    viewing_history = State()
    waiting_for_reply = State()

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
        review_text = f"\n\n💭 Отзыв: {current_item[4]}" if current_item[4] else ""
        admin_response = f"\n\n💬 Ответ администратора: {current_item[5]}" if current_item[5] else ""
        
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
        admin_response = f"\n\n💬 Ответ администратора: {current_item[4]}" if current_item[4] else ""
        
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

async def handle_admin_reply(callback: types.CallbackQuery, state: FSMContext):
    """
    Обрабатывает нажатие на кнопку "Ответить" для отзыва или вопроса.
    
    Args:
        callback (types.CallbackQuery): Объект callback запроса
        state (FSMContext): Контекст состояния FSM
    """
    # Проверяем уровень администратора
    admin_level = (await get_user(callback.from_user.id))[2]
    if admin_level < 2:
        await show_admin_menu(callback.message)
        return

    # Получаем ID элемента и тип истории из callback_data
    parts = callback.data.split("_")
    item_id = int(parts[2])
    history_type = parts[3]
    
    print(f"DATA: {parts}\n"
          f"item_id: {item_id}\n"
          f"history_type: {history_type}\n")

    # Получаем данные отзыва/вопроса из базы
    if history_type == "reviews":
        item = await get_review_by_id(item_id)
        if not item:
            await callback.answer("Отзыв не найден!", show_alert=True)
            return
        # Проверяем наличие ответа
        if item[5]:
            await callback.answer("На этот отзыв уже есть ответ администратора!", show_alert=True)
            return
            
        status = ADMIN_HISTORY_STATUS_WITH_ANSWER if item[5] else ADMIN_HISTORY_STATUS_WITHOUT_ANSWER
        admin_response = f"\n\n💬 Ответ администратора: {item[5]}" if item[5] else ""
        text = ADMIN_HISTORY_REVIEW_TEMPLATE.format(
            review_id=item[0],
            username=item[2],
            status=status,
            date=format_datetime(item[6]),
            rating="⭐" * item[3],
            review_text=f"\n\n💭 Отзыв: {item[4]}" if item[4] else "",
            admin_response=admin_response
        )
    else:
        item = await get_questions_by_id(item_id)
        print(f"ITEM: {item}\n")
        if not item:
            await callback.answer("Вопрос не найден!", show_alert=True)
            return
        # Проверяем наличие ответа
        if item[4]:
            await callback.answer("На этот вопрос уже есть ответ администратора!", show_alert=True)
            return
            
        status = ADMIN_HISTORY_STATUS_WITH_ANSWER if item[4] else ADMIN_HISTORY_STATUS_WITHOUT_ANSWER
        admin_response = f"\n\n💬 Ответ администратора: {item[4]}" if item[4] else ""
        text = ADMIN_HISTORY_QUESTION_TEMPLATE.format(
            question_id=item[0],
            username=item[2], 
            status=status,
            date=format_datetime(item[5]),
            question_text=item[3],
            admin_response=admin_response
        )

    # Сохраняем данные в состоянии
    await state.update_data(
        reply_item_id=item_id,
        reply_history_type=history_type
    )
    
    # Устанавливаем состояние ожидания ответа
    await state.set_state(AdminHistoryStates.waiting_for_reply)

    # Отправляем сообщение с отзывом/вопросом и просьбой ввести ответ
    await callback.message.edit_text(
        f"{text}\n\n✍️ Введите ваш ответ:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(text="❌ Отмена", callback_data="admin_cancel_reply")
        ]])
    )

async def handle_admin_reply_text(message: types.Message, state: FSMContext):
    """
    Обрабатывает текст ответа администратора и сохраняет его в базу данных.
    
    Args:
        message (types.Message): Объект сообщения с ответом
        state (FSMContext): Контекст состояния FSM
    """
    # Получаем сохраненные данные из состояния
    data = await state.get_data()
    item_id = data.get("reply_item_id")
    history_type = data.get("reply_history_type")

    print(f"DATA: {data}\n"
          f"item_id: {item_id}\n"
          f"history_type: {history_type}\n")
    
    # Сохраняем ответ в базу данных
    if history_type == "reviews":
        await add_review_response(item_id, message.text)
    else:
        await add_question_response(item_id, message.text)
    
    # Возвращаемся к просмотру истории
    await state.set_state(AdminHistoryStates.viewing_history)
    
    await delete_last_messages(message.chat.id, message.message_id)

    # Отправляем сообщение об успешном сохранении
    await message.answer(
        "✅ Ответ успешно сохранен!",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(text="◀️ Назад", callback_data=f"back_to_main")
        ]])
    )

async def handle_admin_cancel_reply(callback: types.CallbackQuery, state: FSMContext):
    """
    Обрабатывает отмену ответа администратора.
    
    Args:
        callback (types.CallbackQuery): Объект callback запроса
        state (FSMContext): Контекст состояния FSM
    """
    # Получаем тип истории из состояния
    data = await state.get_data()
    history_type = data.get("reply_history_type")
    
    # Возвращаемся к просмотру истории
    await state.set_state(AdminHistoryStates.viewing_history)
    
    # Отправляем сообщение об отмене
    await callback.message.edit_text(
        "❌ Ответ отменен.",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(text="◀️ Назад", callback_data=f"back_to_main")
        ]])
    )


