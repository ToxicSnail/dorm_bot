import telebot
import os
from pytube import YouTube
import re
import string
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


api = open("api.txt", "r").read()

bot = telebot.TeleBot(api)

USER_STATES = {}
DOWNLOADED_VIDEOS_FILE = "downloaded_videos.txt"

if not os.path.exists(DOWNLOADED_VIDEOS_FILE):
    with open(DOWNLOADED_VIDEOS_FILE, "w", encoding="utf-8") as file:
        pass

def add_to_downloaded_list(video_title):
    with open(DOWNLOADED_VIDEOS_FILE, "a", encoding="utf-8") as file:
        file.write(video_title + "\n")

def sanitize_filename(filename):
    valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
    cleaned_filename = ''.join(c for c in filename if c in valid_chars)
    return cleaned_filename

@bot.message_handler(commands=['start'])
def handle_start(message):
    user_id = message.from_user.id
    USER_STATES[user_id] = "menu"
    send_main_menu(message)

@bot.message_handler(func=lambda message: True)
def handle_text(message):
    user_id = message.from_user.id
    text = message.text.lower()

    if text == "stop":
        handle_stop(message)
    elif USER_STATES.get(user_id) == "menu":
        handle_menu(message)
    elif USER_STATES.get(user_id) == "select_downloaded":
        handle_select_downloaded(message)
    elif USER_STATES.get(user_id) == "yt_link":
        handle_yt_link(message)

def handle_menu(message):
    text = message.text.lower()

    if text == "listen to downloaded":
        handle_play_downloaded(message)
    elif text == "download and listen":
        bot.send_message(message.chat.id, "Please send me the link to the YouTube video you want to download.")
        USER_STATES[message.from_user.id] = "yt_link"
    else:
        send_main_menu(message)

def handle_yt_link(message):
    user_id = message.from_user.id
    text = message.text

    try:
        yt = YouTube(text)
        video_title = sanitize_filename(yt.title)
        message = bot.send_message(message.chat.id, "Starting download...")
        video = yt.streams.get_lowest_resolution()
        file_path = os.path.join(os.getcwd(), f"{video_title}.mp4")
        video.download(filename=file_path)
        bot.edit_message_text("Download complete!", chat_id=message.chat.id, message_id=message.message_id)
        play_video(message.chat.id, file_path)

    except Exception as e:
        bot.send_message(message.chat.id, f"Error: {e}")

    send_main_menu(message)

def handle_play_downloaded(message):
    bot.send_message(message.chat.id, "Here are the downloaded videos:", reply_markup=create_downloaded_markup())
    USER_STATES[message.from_user.id] = "select_downloaded"

def handle_select_downloaded(message):
    selected_option = message.text.strip()

    if selected_option == "Return to Menu":
        send_main_menu(message)
        return

    with open(DOWNLOADED_VIDEOS_FILE, "r", encoding="utf-8") as file:
        downloaded_videos = [line.strip() for line in file.readlines()]

    if selected_option in downloaded_videos:
        file_path = os.path.join(os.getcwd(), f"{selected_option}.mp4")
        play_video(message.chat.id, file_path)
    else:
        bot.send_message(message.chat.id, "Video not found. Please select a video from the list.")
        handle_play_downloaded(message)

def create_downloaded_markup():
    markup = telebot.types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True, one_time_keyboard=True)
    with open(DOWNLOADED_VIDEOS_FILE, "r", encoding="utf-8") as file:
        for video_title in file:
            markup.add(video_title.strip())
    markup.add("Return to Menu")
    return markup

def send_main_menu(message):
    USER_STATES[message.from_user.id] = "menu"
    bot.send_message(message.chat.id, "You're now back in the main menu. How can I assist you further?", reply_markup=create_menu_markup())

def create_menu_markup():
    markup = telebot.types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    markup.add("Listen to downloaded", "Download and listen", "Stop")
    return markup

def handle_stop(message):
    stop_playback()
    bot.send_message(message.chat.id, "Playback stopped.")
    send_main_menu(message)

def stop_playback():
    os.system("pkill vlc")

def play_video(chat_id, file_path):
    try:
        # ??? Windows ???? ????? ????????? ??? "C:\\Program Files\\VideoLAN\\VLC\\vlc.exe"
        # ??? Linux ? macOS ???? ?????? ?????? "vlc"
        os.system(f"vlc --play-and-exit '{file_path}'")  # --play-and-exit ?????????? VLC ????????? ????? ???????????????
    except Exception as e:
        bot.send_message(chat_id, "Failed to play the video.")

bot.polling(none_stop=True)
