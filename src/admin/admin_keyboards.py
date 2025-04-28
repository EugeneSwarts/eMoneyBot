from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from src.messages import BUTTON_BACK, BUTTON_SHOW_ALL, BUTTON_WITHOUT_RESPONSES, BUTTON_SORT_NEW, BUTTON_SORT_OLD, BUTTON_BACK_TO_MAIN, BUTTON_NEXT, BUTTON_PAGE_INFO

def get_admin_menu_keyboard(admin_level: int) -> InlineKeyboardMarkup:
    """
    Создает клавиатуру для меню администратора в зависимости от уровня доступа.
    
    Args:
        admin_level (int): Уровень доступа администратора (1-3)
        
    Returns:
        InlineKeyboardMarkup: Клавиатура для меню администратора
    """
    keyboard_buttons = []

    # Базовые кнопки для всех администраторов (уровень 1+)
    keyboard_buttons.extend([
        [
            InlineKeyboardButton(
                text="📝 Отзывы",
                callback_data="admin_history_reviews"
            ),
            InlineKeyboardButton(
                text="❓ Вопросы", 
                callback_data="admin_history_questions"
            )
        ]
    ])

    # Дополнительные кнопки для уровня 2+
    if admin_level >= 2:
        keyboard_buttons.append([
            InlineKeyboardButton(
                text="📊 Статистика",
                callback_data="admin_stats"
            )
        ])

    # Кнопки управления только для уровня 3
    if admin_level >= 3:
        keyboard_buttons.append([
            InlineKeyboardButton(
                text="👥 Управление пользователями",
                callback_data="admin_users"
            )
        ])

    return InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)


def get_admin_reviews_keyboard() -> InlineKeyboardMarkup:
    """
    Создает клавиатуру для управления отзывами администратора.
    """
    keyboard_buttons = [
        [InlineKeyboardButton(text=BUTTON_SHOW_ALL, callback_data="admin_show_all_reviews")],
        [InlineKeyboardButton(text=BUTTON_WITHOUT_RESPONSES, callback_data="admin_show_all_reviews_without_answers")],
        [InlineKeyboardButton(text="📊 Выгрузить все отзывы в Excel", callback_data="admin_export_reviews_excel")],
        [InlineKeyboardButton(text=BUTTON_BACK, callback_data="back_to_main")]
    ]

    return InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)


def get_admin_questions_keyboard() -> InlineKeyboardMarkup:
    """
    Создает клавиатуру для управления вопросами администратора.
    """
    keyboard_buttons = [
        [InlineKeyboardButton(text=BUTTON_SHOW_ALL, callback_data="admin_show_all_questions")],
        [InlineKeyboardButton(text=BUTTON_WITHOUT_RESPONSES, callback_data="admin_show_all_questions_without_answers")],
        [InlineKeyboardButton(text="📊 Выгрузить все вопросы в Excel", callback_data="admin_export_questions_excel")],
        [InlineKeyboardButton(text=BUTTON_BACK, callback_data="back_to_main")]
    ]

    return InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)


# =============================================
# Клавиатура для выбора сортировки администратора
# =============================================
def get_admin_sort_type_keyboard(history_type: str, filter_type: str) -> InlineKeyboardMarkup:
    """
    Создает клавиатуру для выбора сортировки.
    
    Args:
        history_type (str): Тип истории ('reviews' или 'questions')
        filter_type (str): Тип фильтра ('all' или 'without_answers')
    """
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=BUTTON_SORT_NEW, callback_data=f"admin_sort_new_{history_type}_{filter_type}")],
        [InlineKeyboardButton(text=BUTTON_SORT_OLD, callback_data=f"admin_sort_old_{history_type}_{filter_type}")],
        [InlineKeyboardButton(text=BUTTON_BACK, callback_data=f"admin_back_to_filter_{history_type}")]
    ])
    return keyboard


def get_admin_pagination_keyboard(current_page: int, total_pages: int, history_type: str, filter_type: str) -> InlineKeyboardMarkup:
    """
    Создает клавиатуру с пагинацией для просмотра истории.
    
    Args:
        current_page (int): Текущая страница
        total_pages (int): Общее количество страниц
        history_type (str): Тип истории ('reviews' или 'questions')
        filter_type (str): Тип фильтра ('all' или 'without_answers')
    """
    keyboard_buttons = []
    
    # Кнопки навигации по страницам
    if total_pages > 1:
        row = []
        if current_page > 0:
            row.append(InlineKeyboardButton(
                text="⬅️",
                callback_data=f"admin_page_{current_page-1}_{history_type}_{filter_type}"
            ))
        row.append(InlineKeyboardButton(
            text=f"{current_page + 1}/{total_pages}",
            callback_data="noop"
        ))
        if current_page < total_pages - 1:
            row.append(InlineKeyboardButton(
                text="➡️",
                callback_data=f"admin_page_{current_page+1}_{history_type}_{filter_type}"
            ))
        keyboard_buttons.append(row)
    
    # Кнопки возврата
    keyboard_buttons.append([
        InlineKeyboardButton(
            text=BUTTON_BACK,
            callback_data=f"admin_back_to_sort_{history_type}_{filter_type}"
        )
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)


def get_admin_history_keyboard(
    current_page: int, 
    total_pages: int, 
    history_type: str, 
    filter_type: str,
    has_admin_response: bool,
    admin_level: int,
    item_id: int
) -> InlineKeyboardMarkup:
    """
    Создает клавиатуру для просмотра истории с пагинацией и кнопкой ответа.
    
    Args:
        current_page (int): Текущая страница
        total_pages (int): Общее количество страниц
        history_type (str): Тип истории ('reviews' или 'questions')
        filter_type (str): Тип фильтра ('all' или 'without_answers')
        has_admin_response (bool): Есть ли ответ администратора
        admin_level (int): Уровень доступа администратора
        item_id (int): ID элемента (отзыва или вопроса)
        
    Returns:
        InlineKeyboardMarkup: Клавиатура для просмотра истории
    """
    keyboard_buttons = []
    
    # Добавляем кнопку "Ответить" если нет ответа и уровень админа > 2
    if not has_admin_response and admin_level >= 2:
        keyboard_buttons.append([
            InlineKeyboardButton(
                text="✍️ Ответить",
                callback_data=f"admin_reply_{item_id}_{history_type}"
            )
        ])

    # Кнопки навигации
    nav_buttons = []
    if current_page > 0:
        nav_buttons.append(InlineKeyboardButton(
            text=BUTTON_BACK,
            callback_data=f"admin_page_{current_page-1}_{history_type}_{filter_type}"
        ))
    if current_page < total_pages - 1:
        nav_buttons.append(InlineKeyboardButton(
            text=BUTTON_NEXT,
            callback_data=f"admin_page_{current_page+1}_{history_type}_{filter_type}"
        ))

    if nav_buttons:
        keyboard_buttons.append(nav_buttons)
        
    # Кнопка с номером страницы на отдельной строке
    keyboard_buttons.append([InlineKeyboardButton(
        text=BUTTON_PAGE_INFO.format(page_number=current_page + 1, total_pages=total_pages),
        callback_data="noop"
    )])
    
    # Кнопки возврата
    keyboard_buttons.append([
        InlineKeyboardButton(
            text=BUTTON_BACK_TO_MAIN,
            callback_data=f"back_to_main"
        )
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)