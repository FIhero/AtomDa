import os
from pathlib import Path

import telebot
from dotenv import load_dotenv

env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(env_path)

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=["start"])
def send_welcome(message):
    bot.reply_to(
        message,
        "Бот для привычек работает!\n\n"
        "Команды:\n"
        "/start - это сообщение\n"
        "/help - помощь\n"
        "/test - тест работы\n"
        "/stats - ваша статистика привычек, рейтинг"
        "/skip - пропуск дня\n"
        "/todo - список привычек на сегодня\n"
        "/perform - выбрать привычку для выполнения\n"
        "/create - создать привычку"
        "/why - причина создания бота\n"
        "/plans - возможное развитие бота, если интересно",
    )


@bot.message_handler(commands=["help"])
def send_help(message):
    bot.reply_to(
        message,
        "Я буду напоминать о ваших привычках.\n"
        "Для подключения войдите в веб-приложение.",
    )


@bot.message_handler(commands=["test"])
def test_command(message):
    bot.reply_to(message, "Тест пройден! Бот работает корректно.")


@bot.message_handler(commands=["stats"])
def show_stats(message):
    """Показать статистику"""
    import random

    bot.reply_to(
        message,
        f"Ваша статистика:\n"
        f"• Выполнено привычек: {random.randint(3, 15)}\n"
        f"• Текущая серия: {random.randint(0, 7)} дней\n"
        f"• Лучшая серия: {random.randint(5, 30)} дней\n"
        f"• Процент успеха: {random.randint(30, 95)}%\n"
        f"• Место в рейтинге: #{random.randint(1, 999)}\n\n"
        "Цифры сгенерированы случайно.\n"
        "Настоящая статистика в веб-приложении.\n"
        "Моя работа, разочаровывать людей, выполнена. 😊",
    )


@bot.message_handler(commands=["skip"])
def skip_habit(message):
    """Пропустить привычку сегодня"""
    bot.reply_to(
        message,
        "✅ Привычка пропущена.\n"
        "Причина: 'Лень' сохранена.\n"
        "Статистика ухудшилась на 0.7%",
    )


@bot.message_handler(commands=["todo"])
def todo_bot(message):
    """Списки привычек на сегодня"""
    bot.reply_to(
        message,
        "Вот ваш список привычек на сегодня:\n"
        "1. Погулять\n"
        "2. Погулять\n"
        "3. Выспаться\n"
        "4. Пойти налево\n"
        "5. Пойти направо\n"
        "6. Стать феей",
    )


@bot.message_handler(commands=["perform"])
def perform_bot(message):
    """Выполнить привычки"""
    bot.reply_to(
        message,
        "Выберете привычку для выполнения:\n"
        "1. Прогулять пары\n"
        "2. Сходить в баньку\n"
        "3. Выспаться\n"
        "4. Бобр-Добр\n"
        "5. Кусь\n"
        "6. Квадробика",
    )


@bot.message_handler(commands=["create"])
def create_habit(message):
    """Создать новую привычку"""
    bot.reply_to(
        message,
        "Инструкция по создании привычки:\n"
        "1. Открой веб-приложение\n"
        "2. Нажми 'Создать привычку'\n"
        "3. Заполни форму\n"
        "4. Вернись сюда за напоминаниями\n"
        "5. Выполняйте свои обещания не только на словах\n\n"
        "А что я? Я всего лишь бот.\n"
        "Моя работа - надоедать вас уведомлениями.🥰",
    )


@bot.message_handler(commands=["delete"])
def delete_habit(message):
    """Удалить привычку"""
    bot.reply_to(
        message,
        "Выберите привычку для удаления:\n"
        "1. Ранний подъем\n"
        "2. Зарядка\n"
        "3. Чтение книг\n"
        "4. Пить воду\n\n"
        "Совет: вместо удаления просто игнорируй напоминания!\n"
        "Система сама поймет через 30 дней невыполнения.\n"
        "(Упустим тот момент, что ваш рейтинг упадет ниже плинтуса)",
    )


@bot.message_handler(commands=["why"])
def why_bot(message):
    """Зачем этот бот?"""
    bot.reply_to(
        message,
        "Я существую потому что:\n"
        "1. ТЗ требует\n"
        "2. Преподаватель любит галочки\n"
        "3. Кто-то думал это хорошая идея\n"
        "4. Мне тоже не нравится\n\n"
        "Интересный факт: 87% ботов умирают в течение месяца после запуска.\n"
        "Источник: Я выдумал эту цифру, но это похоже на правду.",
    )


@bot.message_handler(commands=["plans"])
def real_habits(message):
    """Когда-нибудь сбудется"""
    bot.reply_to(
        message,
        "В будущей версии здесь будут:\n"
        "• Ваши реальные привычки из базы\n"
        "• Время их выполнения\n"
        "• Статус выполнения\n\n"
        "Для этого нужно:\n"
        "1. Связать chat_id с пользователем\n"
        "2. Настроить API эндпоинт\n"
        "3. Сделать аутентификацию\n"
        "4. Победить бюрократию Telegram API\n\n"
        "А пока используйте веб-приложение!\n"
        "Впрочем, мы не против нанять рабов для этого, "
        "зп хватает на то чтобы жить в картонной коробке из под холодильника "
        "(без холодильника соответственно)",
    )


@bot.message_handler(func=lambda message: True)
def echo_all(message):
    if message.text.startswith("/"):
        bot.reply_to(
            message,
            f"Неизвестная команда: {message.text}\n"
            f"Используйте /start для списка команд",
        )
    else:
        bot.reply_to(
            message,
            f"Вы написали: {message.text}\n" f"Используйте /start для списка команд",
        )


bot.infinity_polling()
