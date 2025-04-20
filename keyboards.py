# =============================================
# Импорт необходимых библиотек
# =============================================
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from messages import (
    BUTTON_BACK, BUTTON_SHOW_ALL, BUTTON_WITH_RESPONSES,
    BUTTON_SORT_NEW, BUTTON_SORT_OLD, BUTTON_PAGE_INFO, BUTTON_NEXT
)
from database import has_questions_with_responses, has_reviews_with_responses

# =============================================
# Основная клавиатура
# =============================================
def get_main_keyboard() -> InlineKeyboardMarkup:
    """
    Создает основную клавиатуру бота с кнопками для взаимодействия.
    Returns:
        InlineKeyboardMarkup: Объект клавиатуры с настроенными кнопками
    """
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✍️ Оставить отзыв", callback_data="leave_review"),
            InlineKeyboardButton(text="❓ Задать вопрос", callback_data="ask_question")
        ],
        [
            InlineKeyboardButton(text="📋 Мои отзывы и вопросы", callback_data="my_reviews")
        ]
    ])
    return keyboard

# =============================================
# Клавиатура с оценками
# =============================================
def get_star_rating_keyboard() -> InlineKeyboardMarkup:
    """
    Создает клавиатуру с оценками в виде звезд от 1 до 5.
    Returns:
        InlineKeyboardMarkup: Объект клавиатуры с кнопками звезд
    """
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⭐", callback_data="rating_1")],
        [InlineKeyboardButton(text="⭐⭐", callback_data="rating_2")],
        [InlineKeyboardButton(text="⭐⭐⭐", callback_data="rating_3")],
        [InlineKeyboardButton(text="⭐⭐⭐⭐", callback_data="rating_4")],
        [InlineKeyboardButton(text="⭐⭐⭐⭐⭐", callback_data="rating_5")],
        [InlineKeyboardButton(text=BUTTON_BACK, callback_data="back_to_main")]
    ])
    return keyboard

# =============================================
# Клавиатура с опциями для отзыва
# =============================================
def get_review_options_keyboard() -> InlineKeyboardMarkup:
    """
    Создает клавиатуру с опциями для отзыва.
    Returns:
        InlineKeyboardMarkup: Клавиатура с кнопками опций
    """
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Отмена", callback_data="back_to_main")],
        [InlineKeyboardButton(text="📝 Оценить без отзыва", callback_data="skip_review_text")]
    ])
    return keyboard

# =============================================
# Клавиатура для выбора типа истории
# =============================================
def get_history_type_keyboard() -> InlineKeyboardMarkup:
    """
    Создает клавиатуру для выбора типа истории (отзывы или вопросы).
    Returns:
        InlineKeyboardMarkup: Клавиатура с кнопками выбора типа
    """
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📝 Мои отзывы", callback_data="history_reviews"),
            InlineKeyboardButton(text="❓ Мои вопросы", callback_data="history_questions")
        ],
        [InlineKeyboardButton(text=BUTTON_BACK, callback_data="back_to_main")]
    ])
    return keyboard

# =============================================
# Клавиатура для выбора фильтра
# =============================================
async def get_filter_type_keyboard(history_type: str, user_id: int) -> InlineKeyboardMarkup:
    """
    Создает клавиатуру для выбора фильтра (все или только с ответами).
    Показывает кнопку "Только с ответами" только если у пользователя есть отзывы/вопросы с ответами.
    
    Args:
        history_type (str): Тип истории ('reviews' или 'questions')
        user_id (int): ID пользователя
    """
    keyboard = []
    
    # Добавляем кнопку "Показать все"
    keyboard.append([InlineKeyboardButton(text=BUTTON_SHOW_ALL, callback_data=f"filter_all_{history_type}")])
    
    # Проверяем наличие отзывов/вопросов с ответами
    has_responses = False
    if history_type == "reviews":
        has_responses = await has_reviews_with_responses(user_id)
    else:  # questions
        has_responses = await has_questions_with_responses(user_id)
    
    # Добавляем кнопку "Только с ответами" только если есть отзывы/вопросы с ответами
    if has_responses:
        keyboard.append([InlineKeyboardButton(text=BUTTON_WITH_RESPONSES, callback_data=f"filter_responses_{history_type}")])
    
    # Добавляем кнопку возврата
    keyboard.append([InlineKeyboardButton(text=BUTTON_BACK, callback_data="back_to_history")])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

# =============================================
# Клавиатура для выбора сортировки
# =============================================
def get_sort_type_keyboard(history_type: str, filter_type: str) -> InlineKeyboardMarkup:
    """
    Создает клавиатуру для выбора сортировки.
    
    Args:
        history_type (str): Тип истории ('reviews' или 'questions')
        filter_type (str): Тип фильтра ('all' или 'responses')
    """
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=BUTTON_SORT_NEW, callback_data=f"sort_new_{history_type}_{filter_type}")],
        [InlineKeyboardButton(text=BUTTON_SORT_OLD, callback_data=f"sort_old_{history_type}_{filter_type}")],
        [InlineKeyboardButton(text=BUTTON_BACK, callback_data=f"back_to_filter_{history_type}")]
    ])
    return keyboard

# =============================================
# Клавиатура для навигации по страницам
# =============================================
def get_pagination_keyboard(page_number: int, total_pages: int, history_type: str, filter_type: str, sort_type: str) -> InlineKeyboardMarkup:
    """
    Создает клавиатуру для навигации по страницам.
    
    Args:
        page_number (int): Номер текущей страницы
        total_pages (int): Общее количество страниц
        history_type (str): Тип истории ('reviews' или 'questions')
        filter_type (str): Тип фильтра ('all' или 'responses')
        sort_type (str): Тип сортировки ('new' или 'old')
        
    Returns:
        InlineKeyboardMarkup: Клавиатура с кнопками навигации
    """
    keyboard = []
    
    # Кнопки навигации
    nav_buttons = []
    if page_number > 1:
        nav_buttons.append(InlineKeyboardButton(
            text=BUTTON_BACK,
            callback_data=f"page_{page_number-1}_{history_type}_{filter_type}_{sort_type}"
        ))
    if page_number < total_pages:
        nav_buttons.append(InlineKeyboardButton(
            text=BUTTON_NEXT,
            callback_data=f"page_{page_number+1}_{history_type}_{filter_type}_{sort_type}"
        ))
    
    if nav_buttons:
        keyboard.append(nav_buttons)
    
    # Информация о странице
    keyboard.append([InlineKeyboardButton(
        text=BUTTON_PAGE_INFO.format(page_number=page_number, total_pages=total_pages),
        callback_data="noop"
    )])
    
    # Кнопка возврата
    keyboard.append([InlineKeyboardButton(
        text="◀️ Назад к фильтрам",
        callback_data=f"back_to_filter_{history_type}"
    )])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

# =============================================
# Клавиатура с кнопкой "Назад"
# =============================================
def get_back_keyboard(callback_data: str = "back_to_main") -> InlineKeyboardMarkup:
    """
    Создает клавиатуру с кнопкой "Назад".
    
    Args:
        callback_data (str): Данные для callback-запроса
        
    Returns:
        InlineKeyboardMarkup: Клавиатура с кнопкой "Назад"
    """
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=BUTTON_BACK, callback_data=callback_data)]
    ]) 