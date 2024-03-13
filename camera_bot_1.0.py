import os
import threading
import time
from datetime import datetime

import pygame
import pygame.camera
import RPi.GPIO as GPIO
import telebot
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

TOKEN = 'YOUR_BOT_TOKEN'
ADMIN_USER_ID = 1234567890
LED_PIN = 3
PIR_PIN = 11
VIDEO_FILE_FORMAT = '.mkv'

bot = telebot.TeleBot(TOKEN)
pygame.init()
pygame.camera.init()
cam = pygame.camera.Camera("/dev/video0", (640, 426))

is_sensor_enabled = False
is_mute_notifications = False

def setup_gpio():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setwarnings(False)
    GPIO.setup(LED_PIN, GPIO.OUT)
    GPIO.setup(PIR_PIN, GPIO.IN)

def destroy_gpio():
    GPIO.output(LED_PIN, GPIO.LOW)
    GPIO.cleanup()

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
    if os.path.exists(filename):
        bot.send_photo(chat_id, photo=open(filename, 'rb'))
        os.remove(filename)  # Remove the file after sending
    else:
        bot.send_message(chat_id, "Failed to capture photo.")

def send_video(chat_id, filename):
    if os.path.exists(filename):
        bot.send_video(chat_id, open(filename, 'rb'))
        os.remove(filename)  # Remove the file after sending
    else:
        bot.send_message(chat_id, "Failed to capture video.")

def start_sensor(chat_id):
    global is_sensor_enabled
    is_sensor_enabled = True
    bot.send_message(chat_id, "Sensor started.")
    threading.Thread(target=sensor_job, args=(chat_id,)).start()

def stop_sensor(chat_id):
    global is_sensor_enabled
    is_sensor_enabled = False
    bot.send_message(chat_id, "Sensor stopped.")

def sensor_job(chat_id):
    is_recording = False
    while is_sensor_enabled:
        i = GPIO.input(PIR_PIN)
        GPIO.output(LED_PIN, i)

        if i == 1 and not is_recording:
            is_recording = True
            send_photo(chat_id, capture_image())  # Capture and send photo when motion is detected

        if is_recording:
            capture_video()  # Continuously capture video while motion is detected

        if i == 0 and is_recording:
            is_recording = False
            send_video(chat_id, capture_video())  # Capture and send video when motion stops

        time.sleep(0.1)

    bot.send_message(chat_id, "Sensor stopped.")

@bot.message_handler(commands=['start'])
def handle_start(message):
    if message.from_user.id != ADMIN_USER_ID:
        bot.send_message(message.chat.id, "Hello! I am James Brown. How can I assist you?")
    else:
        keyboard = InlineKeyboardMarkup()
        keyboard.row(InlineKeyboardButton("Start Sensor", callback_data='start_sensor'))
        bot.send_message(message.chat.id, "Supported commands:", reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: True)
def handle_button_click(call):
    command = call.data
    chat_id = call.message.chat.id

    if command == 'start_sensor':
        start_sensor(chat_id)
    elif command == 'stop_sensor':
        stop_sensor(chat_id)

def main():
    setup_gpio()
    bot.polling(none_stop=False, interval=5, timeout=20)
    destroy_gpio()

if __name__ == '__main__':
    main()
