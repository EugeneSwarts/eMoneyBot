# =============================================
# Импорт необходимых библиотек
# =============================================
from dotenv import load_dotenv
import os
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

# =============================================
# Загрузка переменных окружения
# =============================================
# Загружаем переменные из файла .env
load_dotenv()

# =============================================
# Конфигурационные параметры
# =============================================
# Токен бота, полученный от @BotFather
# Должен быть указан в файле .env как BOT_TOKEN=your_token_here
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Путь к файлу базы данных SQLite
# База данных будет создана в директории data
DATABASE_PATH = os.path.join("data", "bot_database.db")

# =============================================
# Настройки системы логирования
# =============================================
# Формат логов
LOG_FORMAT = '%(asctime)s | %(levelname)s | %(message)s'
LOG_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
LOG_LEVEL = 'INFO'

# =============================================
# Сообщения для логов
# =============================================
LOG_MESSAGE_DELETE_ERROR = "Не удалось удалить сообщение {message_id}: {error}"
LOG_MESSAGE_EDIT_ERROR = "Не удалось отредактировать сообщение: {error}"
LOG_USER_ACTION = "Пользователь {user_id} нажал кнопку: {callback_data}"
LOG_DB_ERROR = "Ошибка при создании записи: {error}"

# =============================================
# Инициализация бота и диспетчера
# =============================================
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage) 