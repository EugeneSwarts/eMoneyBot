ADMIN_MENU_TEXT = ("🔐 Добро пожаловать в панель администратора! 🌟\n\n"
                  "✨ Здесь вы можете управлять:\n"
                  "📝 Отзывами пользователей\n"
                  "❓ Вопросами от клиентов\n\n"
                  "Выберите нужный раздел для работы ⤵️")

# Сообщения для раздела отзывов
ADMIN_REVIEWS_TEXT = "📝 Раздел управления отзывами\n\nВыберите действие:"
ADMIN_REVIEWS_EMPTY = "📭 Нет новых отзывов для обработки."
ADMIN_REVIEW_APPROVED = "✅ Отзыв одобрен и опубликован."
ADMIN_REVIEW_REJECTED = "❌ Отзыв отклонен."
ADMIN_REVIEW_DELETED = "🗑 Отзыв удален."

# Сообщения для раздела вопросов
ADMIN_QUESTIONS_TEXT = "❓ Раздел управления вопросами\n\nВыберите действие:"
ADMIN_QUESTIONS_EMPTY = "📭 Нет новых вопросов для обработки."
ADMIN_QUESTION_ANSWERED = "✅ Ответ на вопрос отправлен пользователю."
ADMIN_QUESTION_DELETED = "🗑 Вопрос удален."

# Сообщения для раздела статистики
ADMIN_STATS_TEXT = "📊 Статистика бота\n\nВыберите период:"
ADMIN_STATS_DAILY = "📈 Статистика за день"
ADMIN_STATS_WEEKLY = "📊 Статистика за неделю"
ADMIN_STATS_MONTHLY = "📉 Статистика за месяц"

# Сообщения для управления пользователями
ADMIN_USERS_TEXT = "👥 Управление пользователями\n\nВыберите действие:"
ADMIN_USER_BANNED = "🚫 Пользователь заблокирован."
ADMIN_USER_UNBANNED = "✅ Пользователь разблокирован."
ADMIN_USER_ADMIN_ADDED = "👑 Пользователю добавлены права администратора."
ADMIN_USER_ADMIN_REMOVED = "👤 Права администратора удалены у пользователя."

# Сообщения об ошибках
ADMIN_ERROR_NO_RIGHTS = "❌ У вас недостаточно прав для выполнения этого действия."
ADMIN_ERROR_INVALID_COMMAND = "❌ Неверная команда. Используйте меню администратора."
ADMIN_ERROR_USER_NOT_FOUND = "❌ Пользователь не найден."
ADMIN_ERROR_ALREADY_ADMIN = "❌ Пользователь уже является администратором."
ADMIN_ERROR_NOT_ADMIN = "❌ Пользователь не является администратором."
ADMIN_ERROR_ALREADY_BANNED = "❌ Пользователь уже заблокирован."
ADMIN_ERROR_NOT_BANNED = "❌ Пользователь не заблокирован."

ADMIN_REVIEWS_FILTER_TEXT = """
📝 Просмотр отзывов

Выберите тип отображения:
- Все отзывы
- Только без ответов
"""

ADMIN_QUESTIONS_FILTER_TEXT = """
❓ Просмотр вопросов

Выберите тип отображения:
- Все вопросы
- Только без ответов
"""

ADMIN_SORT_TEXT = """
Выберите порядок сортировки:
- Сначала новые
- Сначала старые
"""

# Сообщения для отображения истории
ADMIN_HISTORY_REVIEW_TEMPLATE = """📝 Отзыв №{review_id} от @{username}

🔄 Статус: {status}
─────────────────────

📅 Дата: {date}
⭐ Рейтинг: {rating}
{review_text}
{admin_response}"""

ADMIN_HISTORY_QUESTION_TEMPLATE = """❓ Вопрос №{question_id} от @{username}

🔄 Статус: {status}
─────────────────────

📅 Дата: {date}
❓ Вопрос: {question_text}
{admin_response}"""

ADMIN_HISTORY_NO_REVIEWS = "Нет отзывов для отображения."
ADMIN_HISTORY_NO_QUESTIONS = "Нет вопросов для отображения."
ADMIN_HISTORY_STATUS_WITH_ANSWER = "✅ С ответом"
ADMIN_HISTORY_STATUS_WITHOUT_ANSWER = "⏳ Без ответа"
