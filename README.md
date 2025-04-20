# 🤖 eMoneyBot

Telegram-бот для управления отзывами и вопросами с современным интерфейсом и удобной навигацией.

## ✨ Особенности

- 🌟 Система рейтинга с возможностью оставления отзывов
- ❓ Функционал для задавания вопросов
- 📊 История отзывов и вопросов с фильтрацией и сортировкой
- 🔒 Система защиты от спама
- 🕒 Персонализированные приветствия в зависимости от времени суток
- 📱 Удобный интерфейс с интерактивными кнопками

## 🛠 Технологии

- Python 3.8+
- aiogram 3.3.0
- SQLite (aiosqlite)
- python-dotenv

## ⚙️ Установка

1. Клонируйте репозиторий:
```bash
git clone https://github.com/EugeneSwarts/eMoneyBot
cd eMoneyBot
```

2. Установите зависимости:
```bash
pip install -r requirements.txt
```

3. Создайте файл `.env` и добавьте токен бота:
```
BOT_TOKEN=your_bot_token_here
```

4. Запустите бота:
```bash
python main.py
```

## 🐧 Установка на Linux сервер

### Ubuntu/Debian

1. Обновите систему и установите необходимые пакеты:
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3 python3-pip git
```

2. Клонируйте репозиторий:
```bash
git clone https://github.com/EugeneSwarts/eMoneyBot
cd eMoneyBot
```

3. Установите зависимости:
```bash
pip3 install -r requirements.txt
```

4. Создайте файл `.env` и добавьте токен бота:
```bash
echo "BOT_TOKEN=your_bot_token_here" > .env
```

5. Запустите бота:
```bash
python3 main.py
```

### CentOS/RHEL

1. Обновите систему и установите необходимые пакеты:
```bash
sudo yum update -y
sudo yum install -y python3 python3-pip git
```

2. Клонируйте репозиторий:
```bash
git clone https://github.com/EugeneSwarts/eMoneyBot
cd eMoneyBot
```

3. Установите зависимости:
```bash
pip3 install -r requirements.txt
```

4. Создайте файл `.env` и добавьте токен бота:
```bash
echo "BOT_TOKEN=your_bot_token_here" > .env
```

5. Запустите бота:
```bash
python3 main.py
```

### Arch Linux

1. Обновите систему и установите необходимые пакеты:
```bash
sudo pacman -Syu --noconfirm
sudo pacman -S --noconfirm python python-pip git
```

2. Клонируйте репозиторий:
```bash
git clone https://github.com/EugeneSwarts/eMoneyBot
cd eMoneyBot
```

3. Установите зависимости:
```bash
pip install -r requirements.txt
```

4. Создайте файл `.env` и добавьте токен бота:
```bash
echo "BOT_TOKEN=your_bot_token_here" > .env
```

5. Запустите бота:
```bash
python main.py
```

### Запуск в фоновом режиме (для всех дистрибутивов)

Для запуска бота в фоновом режиме можно использовать `nohup`:

```bash
nohup python3 main.py > bot.log 2>&1 &
```

Для проверки работы бота:
```bash
tail -f bot.log
```

Для остановки бота:
```bash
pkill -f "python3 main.py"
```

## 📁 Структура проекта

```
eMoneyBot/
├── main.py           # Основной файл с логикой бота
├── config.py         # Конфигурационные параметры
├── database.py       # Работа с базой данных
├── keyboards.py      # Клавиатуры и кнопки
├── messages.py       # Текстовые сообщения
├── utils.py          # Вспомогательные функции
├── .env              # Переменные окружения
├── requirements.txt  # Зависимости проекта
└── bot_database.db   # Файл базы данных
```

## 🔑 Основные функции

- **Отзывы**: Пользователи могут оставлять отзывы с рейтингом от 1 до 5 звезд
- **Вопросы**: Возможность задавать вопросы
- **История**: Просмотр истории отзывов и вопросов с фильтрацией и сортировкой
- **Защита**: Система ограничений для предотвращения спама
- **Интерфейс**: Удобная навигация с помощью интерактивных кнопок

## 🤝 Вклад в проект

Приветствуются pull requests. Для крупных изменений, пожалуйста, сначала откройте issue для обсуждения того, что вы хотите изменить.

## 📝 Лицензия

MIT

---

<div align="center">
  <sub>Создано с ❤️ для удобного взаимодействия с покупателями</sub>
</div>