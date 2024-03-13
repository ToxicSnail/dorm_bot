import os
from datetime import datetime

import pygame
import pygame.camera
import telebot
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

TOKEN = open("api.txt", "r").read()

bot = telebot.TeleBot(TOKEN)
pygame.init()
pygame.camera.init()
cam = pygame.camera.Camera("/dev/video0", (640, 426))

VIDEO_FILE_FORMAT = '.mkv'

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

def send_photo(chat_id, filename):
    with open(filename, 'rb') as photo:
        bot.send_photo(chat_id, photo=photo)
    os.remove(filename)  # Remove the file after sending

def send_video(chat_id, filename):
    with open(filename, 'rb') as video:
        bot.send_video(chat_id, video=video)
    os.remove(filename)  # Remove the file after sending

@bot.message_handler(commands=['start'])
def handle_start(message):
    keyboard = InlineKeyboardMarkup()
    keyboard.row(
        InlineKeyboardButton("Сделать фото", callback_data='take_photo'),
        InlineKeyboardButton("Записать видео", callback_data='record_video')
    )
    bot.send_message(message.chat.id, "Выберите действие:", reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    chat_id = call.message.chat.id
    
    if call.data == 'take_photo':
        filename = capture_image()
        send_photo(chat_id, filename)
    elif call.data == 'record_video':
        filename = capture_video()
        send_video(chat_id, filename)

    # Добавляем возможность возвращаться в главное меню после действия
    keyboard = InlineKeyboardMarkup()
    keyboard.row(
        InlineKeyboardButton("Вернуться в главное меню", callback_data='main_menu')
    )
    bot.send_message(chat_id, "Выберите следующее действие:", reply_markup=keyboard)

    # Для обработки возвращения в главное меню
    if call.data == 'main_menu':
        handle_start(call.message)

def main():
    bot.polling(none_stop=True)

if __name__ == '__main__':
    main()
