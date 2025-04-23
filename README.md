# 🤖 eMoneyBot

<div align="center">

![Version](https://img.shields.io/badge/version-0.7.1-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-green.svg)
![License](https://img.shields.io/badge/license-MIT-yellow.svg)

</div>

<div align="center">

Telegram-бот для управления отзывами и вопросами с современным интерфейсом и удобной навигацией.

</div>

## 📑 Навигация

- [✨ Особенности](#-особенности)
- [🛠 Технологии](#-технологии)
- [🤖 Получение токена бота](#-получение-токена-бота)
- [🐧 Установка на Linux сервер](#-установка-на-linux-сервер)
  - [Ubuntu/Debian](#ubuntudebian)
  - [CentOS/RHEL](#centosrhel)
  - [Arch Linux](#arch-linux)
  - [Настройка systemd](#настройка-systemd-рекомендуемый-способ)
- [⚙️ Настройка окружения](#-настройка-окружения)
- [📁 Структура проекта](#-структура-проекта)
- [🔑 Основные функции](#-основные-функции)
- [🤝 Вклад в проект](#-вклад-в-проект)
- [📝 Лицензия](#-лицензия)

## ✨ Особенности

<div align="center">

| Функция | Описание |
|---------|----------|
| 🌟 Рейтинг | Система рейтинга с возможностью оставления отзывов |
| ❓ Вопросы | Функционал для задавания вопросов |
| 📊 История | История отзывов и вопросов с фильтрацией и сортировкой |
| 🔒 Безопасность | Система защиты от спама |
| 🕒 Приветствия | Персонализированные приветствия в зависимости от времени суток |
| 📱 Интерфейс | Удобный интерфейс с интерактивными кнопками |
| 🔄 Асинхронность | Асинхронная обработка запросов |
| 💾 Хранение | Надежное хранение данных в SQLite |

</div>

## 🛠 Технологии

<div align="center">

| Технология | Версия | Описание |
|------------|--------|----------|
| Python | 3.8+ | Основной язык программирования |
| aiogram | 3.3.0 | Асинхронный фреймворк для Telegram Bot API |
| aiosqlite | 0.19.0 | Асинхронная работа с SQLite |
| python-dotenv | 1.0.0 | Управление переменными окружения |

</div>

## 🤖 Получение токена бота

<div align="center">

![BotFather](https://img.shields.io/badge/BotFather-2CA5E0?style=for-the-badge&logo=telegram&logoColor=white)

</div>

1. Откройте Telegram и найдите [@BotFather](https://t.me/BotFather)
2. Начните диалог с командой `/start`
3. Создайте нового бота командой `/newbot`
4. Следуйте инструкциям:
   - Введите имя бота (отображается в контактах)
   - Введите username бота (должен заканчиваться на "bot", например: `my_awesome_bot`)
5. После успешного создания бота, BotFather отправит вам токен в формате:
   ```
   123456789:ABCdefGHIjklMNOpqrsTUVwxyz
   ```
6. Скопируйте полученный токен и вставьте его в файл `.env`:
   ```
   BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
   ```

<div align="center">

⚠️ **Важно**: Никогда не публикуйте токен бота в открытых репозиториях или чатах. Если токен был скомпрометирован, немедленно отзовите его через BotFather командой `/revoke` и создайте нового бота.

</div>

## 🐧 Установка на Linux сервер

### Ubuntu/Debian

<div align="center">

![Ubuntu](https://img.shields.io/badge/Ubuntu-E95420?style=for-the-badge&logo=ubuntu&logoColor=white)
![Debian](https://img.shields.io/badge/Debian-A81D33?style=for-the-badge&logo=debian&logoColor=white)

</div>

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

<div align="center">

![CentOS](https://img.shields.io/badge/CentOS-262577?style=for-the-badge&logo=centos&logoColor=white)
![RHEL](https://img.shields.io/badge/RHEL-EE0000?style=for-the-badge&logo=redhat&logoColor=white)

</div>

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

<div align="center">

![Arch Linux](https://img.shields.io/badge/Arch_Linux-1793D1?style=for-the-badge&logo=arch-linux&logoColor=white)

</div>

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

### Настройка systemd (рекомендуемый способ)

<div align="center">

![Systemd](https://img.shields.io/badge/systemd-000000?style=for-the-badge&logo=systemd&logoColor=white)

</div>

Для обеспечения работы бота 24/7 рекомендуется настроить его как системный сервис с помощью systemd:

1. Создайте файл сервиса:
```bash
sudo nano /etc/systemd/system/emoneybot.service
```

2. Добавьте следующее содержимое:
```ini
[Unit]
Description=eMoneyBot Telegram Bot
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/path/to/eMoneyBot
ExecStart=/usr/bin/python3 /path/to/eMoneyBot/main.py
Restart=always
RestartSec=10
StandardOutput=syslog
StandardError=syslog
SyslogIdentifier=emoneybot
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
```

3. Замените следующие параметры:
   - `your_username` - имя пользователя, от которого будет запущен бот
   - `/path/to/eMoneyBot` - полный путь к директории с ботом

4. Сохраните файл и выполните следующие команды:
```bash
# Перезагрузите конфигурацию systemd
sudo systemctl daemon-reload

# Включите автозапуск сервиса
sudo systemctl enable emoneybot

# Запустите сервис
sudo systemctl start emoneybot
```

5. Проверьте статус сервиса:
```bash
sudo systemctl status emoneybot
```

Полезные команды для управления сервисом:
```bash
# Остановить бота
sudo systemctl stop emoneybot

# Перезапустить бота
sudo systemctl restart emoneybot

# Посмотреть логи
sudo journalctl -u emoneybot -f
```

## ⚙️ Настройка окружения

<div align="center">

![Environment](https://img.shields.io/badge/Environment-4A4A4A?style=for-the-badge&logo=environment&logoColor=white)

</div>

После получения токена бота, необходимо настроить файл `.env`:

1. Создайте файл `.env` в корневой директории проекта:
```bash
# Создание файла .env
touch .env

# Открытие файла в текстовом редакторе
nano .env  # для Linux/Mac
# или
notepad .env  # для Windows
```

2. Добавьте в файл `.env` следующие параметры:
```
# Токен вашего бота (обязательный параметр)
BOT_TOKEN=your_bot_token_here

# Дополнительные настройки (опционально)
ADMIN_ID=123456789  # ID администратора бота
DEBUG=False         # Режим отладки (True/False)
```

<div align="center">

⚠️ **Важно**: 
- Файл `.env` должен находиться в корневой директории проекта
- Не включайте файл `.env` в систему контроля версий (он уже добавлен в .gitignore)
- Храните токен бота в безопасном месте
- Не передавайте файл `.env` третьим лицам

</div>

## 📁 Структура проекта

```
eMoneyBot/
├── main.py           # Основной файл с логикой бота
├── src/              # Исходный код проекта
│   ├── __init__.py   # Инициализация пакета
│   ├── config.py     # Конфигурационные параметры
│   ├── database.py   # Работа с базой данных
│   ├── keyboards.py  # Клавиатуры и кнопки
│   ├── messages.py   # Текстовые сообщения
│   └── utils.py      # Вспомогательные функции
├── data/             # Директория для хранения данных
│   └── bot_database.db   # Файл базы данных
├── .env              # Переменные окружения
├── requirements.txt  # Зависимости проекта
└── README.md         # Документация проекта
```

## 🔑 Основные функции

<div align="center">

| Категория | Функции |
|-----------|---------|
| 📝 Отзывы | • Оставление отзывов с рейтингом от 1 до 5 звезд<br>• Возможность добавления текстового комментария<br>• Просмотр истории своих отзывов |
| ❓ Вопросы | • Задавание вопросов<br>• Просмотр истории вопросов<br>• Фильтрация и сортировка вопросов |
| 🔒 Безопасность | • Защита от спама<br>• Ограничение частоты запросов<br>• Валидация входящих данных |
| 📱 Интерфейс | • Интерактивные кнопки для навигации<br>• Удобное меню команд<br>• Персонализированные приветствия |

</div>

## 🤝 Вклад в проект

<div align="center">

![Contributions](https://img.shields.io/badge/Contributions-Welcome-brightgreen.svg)

</div>

Приветствуются pull requests. Для крупных изменений, пожалуйста, сначала откройте issue для обсуждения того, что вы хотите изменить.

## 📝 Лицензия

<div align="center">

![License](https://img.shields.io/badge/License-MIT-yellow.svg)

</div>

MIT

---

<div align="center">
  <sub>Создано с ❤️ для удобного взаимодействия с покупателями</sub>
</div>