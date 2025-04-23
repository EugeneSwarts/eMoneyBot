from aiogram import types
from aiogram.fsm.context import FSMContext
from .admin_keyboards import get_admin_menu_keyboard
from .admin_messages import ADMIN_MENU_TEXT
from src.database import get_user

async def show_admin_menu(message, user_id: int, is_bot: bool):
    """
    Показывает меню администратора.
    
    Args:
        message: Объект сообщения или callback
        user_id: ID пользователя
        is_bot: Флаг, указывающий, что сообщение отправлено ботом
    """
    # Получаем уровень доступа администратора из базы данных
    user = await get_user(user_id)
    admin_level = user[2] if user else 0  # user[2] - это поле admin_rights в базе данных
    
    if is_bot:
        await message.edit_text(
            ADMIN_MENU_TEXT,
            reply_markup=get_admin_menu_keyboard(admin_level)
        )
    else:
        await message.answer(
            ADMIN_MENU_TEXT,
            reply_markup=get_admin_menu_keyboard(admin_level)
        ) 