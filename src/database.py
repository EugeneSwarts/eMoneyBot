import aiosqlite
from src.config import DATABASE_PATH, SUPER_ADMIN_ID
from datetime import datetime

# =============================================
# Инициализация базы данных
# =============================================
async def init_db():
    """
    Инициализирует базу данных и создает необходимые таблицы, если они не существуют.
    Создает таблицу users со следующими полями:
    - user_id: ID пользователя в Telegram (первичный ключ)
    - username: Имя пользователя
    - admin_level: Уровень доступа администратора
    - is_banned: Статус блокировки
    - ban_reason: Причина блокировки
    """
    async with aiosqlite.connect(DATABASE_PATH) as db:
        # Таблица пользователей
        await db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                admin_level INTEGER DEFAULT 0,
                is_banned BOOLEAN DEFAULT 0,
                ban_reason TEXT DEFAULT NULL
            )
        ''')
        
        # Таблица отзывов
        await db.execute('''
            CREATE TABLE IF NOT EXISTS reviews (
                review_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                username TEXT,
                rating INTEGER NOT NULL,
                review_text TEXT,
                admin_response TEXT,
                created_at TIMESTAMP NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        ''')
        
        # Таблица вопросов
        await db.execute('''
            CREATE TABLE IF NOT EXISTS questions (
                question_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                username TEXT,
                question_text TEXT NOT NULL,
                admin_response TEXT,
                created_at TIMESTAMP NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        ''')
        await db.commit()
        
        # Проверяем и обновляем права супер-администратора
        await check_super_admin()

async def check_super_admin():
    """
    Проверяет и обновляет права супер-администратора.
    Если пользователь с ID из SUPER_ADMIN_ID существует, но его уровень админки не 4,
    то устанавливает уровень 4.
    """
    if not SUPER_ADMIN_ID:
        return
        
    async with aiosqlite.connect(DATABASE_PATH) as db:
        # Проверяем существование пользователя
        async with db.execute(
            'SELECT admin_level FROM users WHERE user_id = ?',
            (SUPER_ADMIN_ID,)
        ) as cursor:
            user = await cursor.fetchone()
            
            if user:
                # Если пользователь существует, но уровень не 4, обновляем
                if user[0] != 4:
                    await db.execute(
                        'UPDATE users SET admin_level = 4 WHERE user_id = ?',
                        (SUPER_ADMIN_ID,)
                    )
                    await db.commit()
            else:
                # Если пользователь не существует, создаем с уровнем 4
                await db.execute(
                    'INSERT INTO users (user_id, admin_level) VALUES (?, 4)',
                    (SUPER_ADMIN_ID,)
                )
                await db.commit()

# =============================================
# Операции с пользователями
# =============================================
async def add_user(user_id: int, username: str):
    """
    Добавляет нового пользователя в базу данных.
    Если пользователь уже существует, операция игнорируется (INSERT OR IGNORE).

    Args:
        user_id (int): ID пользователя в Telegram
        username (str): Имя пользователя
    """
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute(
            'INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)',
            (user_id, username)
        )
        await db.commit()

async def get_user(user_id: int):
    """
    Получает информацию о пользователе по его ID.

    Args:
        user_id (int): ID пользователя в Telegram

    Returns:
        tuple: Кортеж с данными пользователя (user_id, username, admin_level, is_banned, ban_reason)
        или None, если пользователь не найден
    """
    async with aiosqlite.connect(DATABASE_PATH) as db:
        async with db.execute(
            'SELECT * FROM users WHERE user_id = ?',
            (user_id,)
        ) as cursor:
            return await cursor.fetchone()

# =============================================
# Управление блокировкой пользователей
# =============================================
async def ban_user(user_id: int, reason: str):
    """
    Блокирует пользователя и устанавливает причину блокировки.

    Args:
        user_id (int): ID пользователя в Telegram
        reason (str): Причина блокировки
    """
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute(
            'UPDATE users SET is_banned = 1, ban_reason = ? WHERE user_id = ?',
            (reason, user_id)
        )
        await db.commit()

async def unban_user(user_id: int):
    """
    Разблокирует пользователя и удаляет причину блокировки.

    Args:
        user_id (int): ID пользователя в Telegram
    """
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute(
            'UPDATE users SET is_banned = 0, ban_reason = NULL WHERE user_id = ?',
            (user_id,)
        )
        await db.commit()

# =============================================
# Управление отзывами
# =============================================
async def create_review(user_id: int, username: str, rating: int, review_text: str = None):
    """
    Создает новый отзыв.

    Args:
        user_id (int): ID пользователя
        username (str): Имя пользователя
        rating (int): Оценка (1-5)
        review_text (str, optional): Текст отзыва
        
    Returns:
        int: ID созданного отзыва
    """
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute(
            '''INSERT INTO reviews (user_id, username, rating, review_text, created_at)
               VALUES (?, ?, ?, ?, ?)
               RETURNING review_id''',
            (user_id, username, rating, review_text, datetime.now())
        )
        review_id = (await cursor.fetchone())[0]
        await db.commit()
        return review_id

async def add_review_response(review_id: int, response: str):
    """
    Добавляет ответ администратора на отзыв.

    Args:
        review_id (int): ID отзыва
        response (str): Текст ответа администратора
    """
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute(
            'UPDATE reviews SET admin_response = ? WHERE review_id = ?',
            (response, review_id)
        )
        await db.commit()

async def can_leave_review_today(user_id: int) -> bool:
    """
    Проверяет, может ли пользователь оставить отзыв сегодня.
    
    Args:
        user_id (int): ID пользователя
        
    Returns:
        bool: True если пользователь может оставить отзыв, False если уже оставлял сегодня
    """
    async with aiosqlite.connect(DATABASE_PATH) as db:
        # Получаем дату последнего отзыва пользователя
        async with db.execute(
            "SELECT created_at FROM reviews WHERE user_id = ? ORDER BY created_at DESC LIMIT 1",
            (user_id,)
        ) as cursor:
            last_review = await cursor.fetchone()
            
            if not last_review:
                return True  # Если отзывов нет, можно оставить
                
            last_review_date = datetime.fromisoformat(last_review[0])
            today = datetime.now()
            
            # Проверяем, что последний отзыв был не сегодня
            return last_review_date.date() < today.date()

async def get_user_reviews(user_id: int, with_responses_only: bool = False, sort_by_date: bool = True):
    """
    Получает отзывы пользователя с возможностью фильтрации и сортировки.
    Если запрошены только отзывы с ответами, но их нет, автоматически возвращает все отзывы.
    
    Args:
        user_id (int): ID пользователя
        with_responses_only (bool): Если True, возвращает только отзывы с ответами
        sort_by_date (bool): Если True, сортирует по дате (новые сверху)
        
    Returns:
        list: Список отзывов пользователя
    """
    async with aiosqlite.connect(DATABASE_PATH) as db:
        # Сначала проверяем, есть ли отзывы с ответами, если запрошены только они
        if with_responses_only:
            query = "SELECT * FROM reviews WHERE user_id = ? AND admin_response IS NOT NULL"
            async with db.execute(query, (user_id,)) as cursor:
                items = await cursor.fetchall()
                if not items:  # Если нет отзывов с ответами, возвращаем все отзывы
                    with_responses_only = False
        
        query = "SELECT * FROM reviews WHERE user_id = ?"
        if with_responses_only:
            query += " AND admin_response IS NOT NULL"
        if sort_by_date:
            query += " ORDER BY created_at DESC"
        async with db.execute(query, (user_id,)) as cursor:
            return await cursor.fetchall()

# =============================================
# Управление вопросами
# =============================================
async def create_question(user_id: int, username: str, question_text: str):
    """
    Создает новый вопрос.

    Args:
        user_id (int): ID пользователя
        username (str): Имя пользователя
        question_text (str): Текст вопроса
        
    Returns:
        int: ID созданного вопроса
    """
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute(
            '''INSERT INTO questions (user_id, username, question_text, created_at)
               VALUES (?, ?, ?, ?)
               RETURNING question_id''',
            (user_id, username, question_text, datetime.now())
        )
        question_id = (await cursor.fetchone())[0]
        await db.commit()
        return question_id

async def add_question_response(question_id: int, response: str):
    """
    Добавляет ответ администратора на вопрос.

    Args:
        question_id (int): ID вопроса
        response (str): Текст ответа администратора
    """
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute(
            'UPDATE questions SET admin_response = ? WHERE question_id = ?',
            (response, question_id)
        )
        await db.commit()

async def get_user_questions(user_id: int, with_responses_only: bool = False, sort_by_date: bool = True):
    """
    Получает вопросы пользователя с возможностью фильтрации и сортировки.
    Если запрошены только вопросы с ответами, но их нет, автоматически возвращает все вопросы.
    
    Args:
        user_id (int): ID пользователя
        with_responses_only (bool): Если True, возвращает только вопросы с ответами
        sort_by_date (bool): Если True, сортирует по дате (новые сверху)
        
    Returns:
        list: Список вопросов пользователя
    """
    async with aiosqlite.connect(DATABASE_PATH) as db:
        # Сначала проверяем, есть ли вопросы с ответами, если запрошены только они
        if with_responses_only:
            query = "SELECT * FROM questions WHERE user_id = ? AND admin_response IS NOT NULL"
            async with db.execute(query, (user_id,)) as cursor:
                items = await cursor.fetchall()
                if not items:  # Если нет вопросов с ответами, возвращаем все вопросы
                    with_responses_only = False
        
        query = "SELECT * FROM questions WHERE user_id = ?"
        if with_responses_only:
            query += " AND admin_response IS NOT NULL"
        if sort_by_date:
            query += " ORDER BY created_at DESC"
        async with db.execute(query, (user_id,)) as cursor:
            return await cursor.fetchall()

async def has_reviews_with_responses(user_id: int) -> bool:
    """
    Проверяет, есть ли у пользователя отзывы с ответами.
    
    Args:
        user_id (int): ID пользователя
        
    Returns:
        bool: True если есть отзывы с ответами, False если нет
    """
    async with aiosqlite.connect(DATABASE_PATH) as db:
        query = "SELECT COUNT(*) FROM reviews WHERE user_id = ? AND admin_response IS NOT NULL"
        async with db.execute(query, (user_id,)) as cursor:
            count = await cursor.fetchone()
            return count[0] > 0

async def has_questions_with_responses(user_id: int) -> bool:
    """
    Проверяет, есть ли у пользователя вопросы с ответами.
    
    Args:
        user_id (int): ID пользователя
        
    Returns:
        bool: True если есть вопросы с ответами, False если нет
    """
    async with aiosqlite.connect(DATABASE_PATH) as db:
        query = "SELECT COUNT(*) FROM questions WHERE user_id = ? AND admin_response IS NOT NULL"
        async with db.execute(query, (user_id,)) as cursor:
            count = await cursor.fetchone()
            return count[0] > 0

async def get_all_reviews(filter_type: str = "all") -> list:
    """
    Получает все отзывы с возможностью фильтрации.
    
    Args:
        filter_type (str): Тип фильтрации ('all' или 'without_answers')
        
    Returns:
        list: Список отзывов
    """
    query = "SELECT * FROM reviews"
    if filter_type == "without_answers":
        query += " WHERE admin_response IS NULL"
    query += " ORDER BY created_at DESC"
    
    async with aiosqlite.connect(DATABASE_PATH) as db:
        async with db.execute(query) as cursor:
            return await cursor.fetchall()

async def get_all_questions(filter_type: str = "all") -> list:
    """
    Получает все вопросы с возможностью фильтрации.
    
    Args:
        filter_type (str): Тип фильтрации ('all' или 'without_answers')
        
    Returns:
        list: Список вопросов
    """
    query = "SELECT * FROM questions"
    if filter_type == "without_answers":
        query += " WHERE admin_response IS NULL"
    query += " ORDER BY created_at DESC"
    
    async with aiosqlite.connect(DATABASE_PATH) as db:
        async with db.execute(query) as cursor:
            return await cursor.fetchall()

async def get_review_by_id(review_id: int):
    """
    Получает отзыв по его ID.
    
    Args:
        review_id (int): ID отзыва
        
    Returns:
        tuple: Данные отзыва или None, если отзыв не найден
    """
    async with aiosqlite.connect(DATABASE_PATH) as db:
        async with db.execute(
            'SELECT * FROM reviews WHERE review_id = ?',
            (review_id,)
        ) as cursor:
            return await cursor.fetchone()

async def get_questions_by_id(question_id: int):
    """
    Получает вопрос по его ID.
    
    Args:
        question_id (int): ID вопроса
        
    Returns:
        tuple: Данные вопроса или None, если вопрос не найден
    """
    async with aiosqlite.connect(DATABASE_PATH) as db:
        async with db.execute(
            'SELECT * FROM questions WHERE question_id = ?',
            (question_id,)
        ) as cursor:
            return await cursor.fetchone()
