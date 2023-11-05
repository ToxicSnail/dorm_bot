import telebot
import os
import time
import webbrowser
import subprocess
from telebot import types

api = open("api.txt", "r").read()

bot = telebot.TeleBot(api)

# Словарь для хранения ссылок на YouTube
youtube_links = {}

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def handle_start(message):
    user_id = message.from_user.id
    youtube_links[user_id] = []
    with open(f"youtube_links_{user_id}.txt", "w") as file:
        file.write("")
    bot.send_message(message.chat.id,
                     f"Привет, {message.from_user.first_name}! Я бот, который работает с видео на YouTube. "
                     "Пожалуйста, отправьте ссылку на видео YouTube или используйте /help, чтобы узнать больше.")

# Обработчик команды /help
@bot.message_handler(commands=['help'])
def handle_help(message):
    bot.send_message(message.chat.id,
                     "Привет! Я бот для работы с видео на YouTube. Вот что я могу:\n"
                     "/start - начать процесс работы с видео\n"
                     "/help - показать это сообщение с инструкциями\n"
                     "/stop - остановить проигрывание видео (если активно)\n"
                     "/list - просмотреть список отправленных ссылок\n"
                     "/clear - очистить список отправленных ссылок\n"
                     "Просто отправьте мне ссылку на видео YouTube, и я открою ее для вас.")

# Обработчик команды /stop
@bot.message_handler(commands=['stop'])
def handle_stop(message):
    user_id = message.from_user.id
    if user_id in youtube_links:
        try:
            subprocess.Popen("taskkill /f /im chrome.exe", shell=True)
            bot.send_message(message.chat.id, "Проигрывание остановлено.")
        except Exception as e:
            print(f"Ошибка при остановке проигрывания: {e}")
        del youtube_links[user_id]
    else:
        bot.send_message(message.chat.id, "Проигрывание видео не активно.")

# Обработчик текстовых сообщений
@bot.message_handler(func=lambda message: True)
def handle_text(message):
    user_id = message.from_user.id
    text = message.text

    # Проверяем, что сообщение похоже на ссылку YouTube
    if 'youtube.com/watch' in text or 'youtu.be/' in text:
        if user_id not in youtube_links:
            youtube_links[user_id] = []

        youtube_links[user_id].append(text)
        with open(f"youtube_links_{user_id}.txt", "a") as file:
            file.write(text + "\n")

        subprocess.Popen("taskkill /f /im chrome.exe", shell=True)
        time.sleep(2)
        # Открываем новую вкладку в браузере Chromium с параметром "autoplay=1"
        webbrowser.open(text + "?autoplay=1")  # Предполагается, что "chromium" это имя, под которым Chromium зарегистрирован
        time.sleep(5)
        webbrowser.open(text + "?autoplay=1")
    else:
        bot.send_message(message.chat.id, "Пожалуйста, отправьте действительную ссылку на видео YouTube.")

# Обработчик команды /list
@bot.message_handler(commands=['list'])
def handle_list(message):
    user_id = message.from_user.id
    if user_id in youtube_links:
        links = youtube_links[user_id]
        if links:
            bot.send_message(message.chat.id, "Ваши отправленные ссылки на YouTube:")
            for i, link in enumerate(links, 1):
                bot.send_message(message.chat.id, f"{i}. {link}")
        else:
            bot.send_message(message.chat.id, "Вы пока не отправили ни одной ссылки на YouTube.")
    else:
        bot.send_message(message.chat.id, "Вы пока не отправили ни одной ссылки на YouTube.")

# Обработчик команды /clear
@bot.message_handler(commands=['clear'])
def handle_clear(message):
    user_id = message.from_user.id
    if user_id in youtube_links:
        youtube_links[user_id] = []
        with open(f"youtube_links_{user_id}.txt", "w") as file:
            file.write("")
        bot.send_message(message.chat.id, "Список отправленных ссылок очищен.")
    else:
        bot.send_message(message.chat.id, "У вас нет отправленных ссылок для очистки.")

# Запуск бота
bot.polling(none_stop=True)
