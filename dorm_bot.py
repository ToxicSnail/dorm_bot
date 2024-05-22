import telebot
import os
import pygame
import pygame.camera
from datetime import datetime
from pytube import YouTube
import re
import string
import sys
import io
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup
from cryptography.fernet import Fernet

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

TOKEN = open("api.txt", "r").read()
bot = telebot.TeleBot(TOKEN)

pygame.init()
pygame.camera.init()
cam = pygame.camera.Camera("/dev/video0", (640, 426))
VIDEO_FILE_FORMAT = '.mkv'
USER_STATES = {}
DOWNLOADED_VIDEOS_FILE = "downloaded_videos.txt"

if not os.path.exists(DOWNLOADED_VIDEOS_FILE):
    with open(DOWNLOADED_VIDEOS_FILE, "w", encoding="utf-8") as file:
        pass

def capture_image():
    filename = datetime.now().strftime('%Y-%m-%d_%H-%M-%S') + '.jpg'
    cam.start()
    pygame.image.save(cam.get_image(), filename)
    cam.stop()
    return filename

def capture_video():
    filename = datetime.now().strftime('%Y-%m-%d_%H-%M-%S') + VIDEO_FILE_FORMAT
    os.system(f"ffmpeg -f v4l2 -framerate 25 -video_size 640x426 -i /dev/video0 -t 5 -c copy \"{filename}\"")
    return filename

def add_to_downloaded_list(video_title):
    with open(DOWNLOADED_VIDEOS_FILE, "a", encoding="utf-8") as file:
        file.write(video_title + "\n")

def sanitize_filename(filename):
    valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
    cleaned_filename = ''.join(c for c in filename if c in valid_chars)
    return cleaned_filename

def send_main_menu(message):
    keyboard = InlineKeyboardMarkup()
    keyboard.row(
        InlineKeyboardButton("Работа с камерой", callback_data='camera'),
        InlineKeyboardButton("Работа с музыкой", callback_data='music')
    )
    bot.send_message(message.chat.id, "Привет! Выберите действие:", reply_markup=keyboard)

def load_key():
    return open("secret.key", "rb").read()

def load_encrypted_password():
    with open("secret.txt", "rb") as file:
        return file.read()

def decrypt_password(encrypted_password, key):
    fernet = Fernet(key)
    return fernet.decrypt(encrypted_password).decode()

key = load_key()
encrypted_password = load_encrypted_password()
real_password = decrypt_password(encrypted_password, key)

@bot.message_handler(commands=['start'])
def handle_start(message):
    msg = bot.send_message(message.chat.id, 'Введите пароль для доступа к боту:')
    bot.register_next_step_handler(msg, check_password)

def check_password(message):
    if message.text == real_password:
        bot.send_message(message.chat.id, "Пароль верный. Доступ разрешен.")
    else:
        bot.send_message(message.chat.id, "Неверный пароль. Доступ запрещен.")

@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    chat_id = call.message.chat.id
    if call.data == 'camera':
        keyboard = InlineKeyboardMarkup()
        keyboard.row(
            InlineKeyboardButton("Сделать фото", callback_data='take_photo'),
            InlineKeyboardButton("Записать видео", callback_data='record_video')
        )
        keyboard.row(InlineKeyboardButton("Вернуться в главное меню", callback_data='main_menu'))
        bot.send_message(chat_id, "Выберите действие:", reply_markup=keyboard)
    elif call.data in ['take_photo', 'record_video']:
        if call.data == 'take_photo':
            filename = capture_image()
            with open(filename, 'rb') as photo:
                bot.send_photo(chat_id, photo=photo)
            os.remove(filename)  
        elif call.data == 'record_video':
            filename = capture_video()
            with open(filename, 'rb') as video:
                bot.send_video(chat_id, video=video)
            os.remove(filename)  
        send_main_menu(call.message)
    elif call.data == 'music':
        markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        markup.add("Слушать скаченное", "Скачать и слушать", "Остановить воспроизведение", "Вернуться в главное меню")
        bot.send_message(chat_id, "Выберите опцию:", reply_markup=markup)
        USER_STATES[chat_id] = 'music_menu'
    
    elif call.data == 'main_menu':
        send_main_menu(call.message)

@bot.message_handler(func=lambda message: USER_STATES.get(message.chat.id) == 'music_menu')
def music_menu(message):
    chat_id = message.chat.id
    if message.text == "Слушать скаченное":
        send_downloaded_list(message)
    elif message.text == "Скачать и слушать":
        msg = bot.send_message(chat_id, "Пожалуйста, отправьте ссылку на видео с YouTube.")
        USER_STATES[chat_id] = 'download_music'
    elif message.text == "Остановить воспроизведение":
        stop_playback()
        bot.send_message(chat_id, "Воспроизведение остановлено.")
        send_main_menu(message)
    elif message.text == "Вернуться в главное меню":
        USER_STATES[chat_id] = None
        send_main_menu(message)

@bot.message_handler(func=lambda message: USER_STATES.get(message.chat.id) == 'download_music')
def download_music(message):
    chat_id = message.chat.id
    try:
        yt = YouTube(message.text)
        video_title = sanitize_filename(yt.title)
        video = yt.streams.get_lowest_resolution()
        file_path = os.path.join(os.getcwd(), f"{video_title}.mp4")
        video.download(filename=file_path)
        add_to_downloaded_list(video_title)
        bot.send_message(chat_id, "Видео успешно скачано.")
    except Exception as e:
        bot.send_message(chat_id, f"Произошла ошибка: {e}")
    USER_STATES[chat_id] = None
    send_main_menu(message)

def send_downloaded_list(message):
    chat_id = message.chat.id
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    with open(DOWNLOADED_VIDEOS_FILE, "r", encoding="utf-8") as file:
        for video_title in file:
            markup.add(video_title.strip())
    markup.add("Вернуться в главное меню")
    bot.send_message(chat_id, "Выберите видео для воспроизведения:", reply_markup=markup)
    USER_STATES[chat_id] = 'play_downloaded'

@bot.message_handler(func=lambda message: USER_STATES.get(message.chat.id) == 'play_downloaded')
def play_downloaded(message):
    chat_id = message.chat.id
    selected_option = message.text
    if selected_option == "Вернуться в главное меню":
        USER_STATES[chat_id] = None
        send_main_menu(message)
        return
    file_path = os.path.join(os.getcwd(), f"{selected_option}.mp4")
    try:
        os.system(f"vlc --play-and-exit '{file_path}'")
        bot.send_message(chat_id, f"Воспроизведение {selected_option}")
    except Exception as e:
        bot.send_message(chat_id, "Не удалось воспроизвести видео.")
    USER_STATES[chat_id] = None
    send_main_menu(message)

def stop_playback():
    os.system("pkill vlc")

if __name__ == '__main__':
    bot.polling(none_stop=True)