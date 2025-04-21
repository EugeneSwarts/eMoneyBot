from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from src.database import get_user

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
    keyboard_buttons = []

    # Базовые кнопки для всех администраторов (уровень 1+)
    keyboard_buttons.extend([
        [
            InlineKeyboardButton(
                text="📝 Отзывы",
                callback_data="admin_reviews"
            ),
            InlineKeyboardButton(
                text="❓ Вопросы", 
                callback_data="admin_questions"
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

    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
    
    admin_menu_text = ("🔐 Добро пожаловать в панель администратора! 🌟\n\n"
                      "✨ Здесь вы можете управлять:\n"
                      "📝 Отзывами пользователей\n"
                      "❓ Вопросами от клиентов\n\n"
                      "Выберите нужный раздел для работы ⤵️")

    if is_bot:
        # Если это callback, редактируем существующее сообщение
        if isinstance(message, types.CallbackQuery):
            await message.message.edit_text(admin_menu_text, reply_markup=keyboard)
        else:
            await message.edit_text(admin_menu_text, reply_markup=keyboard)
    else:
        # Если обычное сообщение, отправляем новое
        await message.answer(admin_menu_text, reply_markup=keyboard)
    
    return True

