from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from src.database import get_user

async def show_admin_menu(message: types.Message):
    """
    Отображает главное меню администратора.
    Доступно только для пользователей с правами администратора.
    
    Args:
        message (types.Message): Объект сообщения от пользователя
        
    Returns:
        bool: True если меню показано успешно, False если нет прав администратора
    """
    # Проверяем права администратора
    user = await get_user(message.from_user.id)
    if not user or user[2] == 0:  # admin_level == 0
        await message.answer("⛔️ У вас нет прав администратора")
        return False

    # Создаем клавиатуру для админ-меню
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="📊 Статистика",
                callback_data="admin_stats"
            )
        ],
        [
            InlineKeyboardButton(
                text="📝 Отзывы",
                callback_data="admin_reviews"
            ),
            InlineKeyboardButton(
                text="❓ Вопросы",
                callback_data="admin_questions"
            )
        ],
        [
            InlineKeyboardButton(
                text="👥 Управление пользователями",
                callback_data="admin_users"
            )
        ]
    ])

    await message.answer(
        "🔐 Панель администратора\n\n"
        "Выберите нужный раздел:",
        reply_markup=keyboard
    )
    return True

