import telebot
import os
import time
from selenium import webdriver
from telebot import types

api = open("api.txt", "r").read()

bot = telebot.TeleBot(api)

# Dictionary to store YouTube links
youtube_links = {}

# User states
MENU_STATE = "menu"
YT_MENU_STATE = "yt_menu"
YT_LINK_STATE = "yt_link"
YT_RANDOM_GENRE_STATE = "yt_random_genre"
YT_PLAYING_STATE = "yt_playing"

# Dictionary to store the current playing status
playing_status = {}


# Command handler /start
@bot.message_handler(commands=['start'])
def handle_start(message):
    user_id = message.from_user.id
    youtube_links[user_id] = []
    playing_status[user_id] = False
    set_user_state(user_id, MENU_STATE)

    # Keyboard with the button "Play music from YouTube"
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item = types.KeyboardButton("Play music from YouTube")
    markup.add(item)

    bot.send_message(message.chat.id,
                     f"Hello, {message.from_user.first_name}! I'm a bot that works with YouTube videos. "
                     "Please choose an action:",
                     reply_markup=markup)


# Command handler /help
@bot.message_handler(commands=['help'])
def handle_help(message):
    bot.send_message(message.chat.id,
                     "Hello! I'm a bot for working with YouTube videos. Here's what I can do:\n"
                     "/start - start the process of working with videos\n"
                     "/help - show this message with instructions\n"
                     "/list - view the list of sent links\n"
                     "/clear - clear the list of sent links\n"
                     "Simply send me a link to a YouTube video, and I'll play it for you.")


# Text message handler
@bot.message_handler(func=lambda message: True)
def handle_text(message):
    user_id = message.from_user.id
    text = message.text

    if get_user_state(user_id) == MENU_STATE:
        handle_menu(message)
    elif get_user_state(user_id) == YT_MENU_STATE:
        handle_yt_menu(message)
    elif get_user_state(user_id) == YT_LINK_STATE:
        handle_yt_link(message)
    elif get_user_state(user_id) == YT_RANDOM_GENRE_STATE:
        handle_yt_random_genre(message)
    elif get_user_state(user_id) == YT_PLAYING_STATE:
        handle_stop(message)


# Menu handler
def handle_menu(message):
    user_id = message.from_user.id
    text = message.text

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("Play a specific video/music from YouTube")
    item2 = types.KeyboardButton("Random")
    item3 = types.KeyboardButton("/stop")
    item4 = types.KeyboardButton("Return to the main menu")

    markup.row(item1, item2)
    markup.row(item3, item4)

    bot.send_message(message.chat.id, "Choose which music you want to play:", reply_markup=markup)
    set_user_state(user_id, YT_MENU_STATE)


# Menu handler for YouTube options
def handle_yt_menu(message):
    user_id = message.from_user.id
    text = message.text

    if text == "Play a specific video/music from YouTube":
        bot.send_message(message.chat.id, "Please send me a link to a YouTube video:")
        set_user_state(user_id, YT_LINK_STATE)
    elif text == "Random":
        bot.send_message(message.chat.id, "Enter the genre for random music:")
        set_user_state(user_id, YT_RANDOM_GENRE_STATE)
    elif text == "/stop":
        handle_stop(message)
    elif text == "Return to the main menu":
        set_user_state(user_id, MENU_STATE)
        handle_start(message)


# Link input handler for YouTube music
def handle_yt_link(message):
    user_id = message.from_user.id
    text = message.text

    # Check if the message looks like a YouTube link
    if 'youtube.com/watch' in text or 'youtu.be/' in text:
        if user_id not in youtube_links:
            youtube_links[user_id] = []

        youtube_links[user_id].append(text)
        with open(f"youtube_links_{user_id}.txt", "a") as file:
            file.write(text + "\n")

        stop_playing(user_id)
        # Open a new tab in the browser with the parameter "autoplay=1"
        driver = webdriver.Chrome()
        driver.get(text + "?autoplay=1")
        playing_status[user_id] = True
        set_user_state(user_id, YT_PLAYING_STATE)
    else:
        bot.send_message(message.chat.id, "Please send a valid YouTube video link.")

    # Return the user to the main menu
    set_user_state(user_id, MENU_STATE)


# Random music genre input handler
def handle_yt_random_genre(message):
    user_id = message.from_user.id
    text = message.text

    # Implement logic to play random video from YouTube based on the genre
    bot.send_message(message.chat.id, f"Playing random music from the genre: {text} (not implemented yet).")

    # Return the user to the main menu
    set_user_state(user_id, MENU_STATE)


# Stop playback handler
def handle_stop(message):
    user_id = message.from_user.id

    if user_id in playing_status and playing_status[user_id]:
        playing_status[user_id] = False
        set_user_state(user_id, MENU_STATE)
        bot.send_message(message.chat.id, "Playback stopped.")
    else:
        bot.send_message(message.chat.id, "Playback is not active.")


# Command handler /list
@bot.message_handler(commands=['list'])
def handle_list(message):
    user_id = message.from_user.id
    if user_id in youtube_links:
        links = youtube_links[user_id]
        if links:
            bot.send_message(message.chat.id, "Your sent YouTube links:")
            for i, link in enumerate(links, 1):
                bot.send_message(message.chat.id, f"{i}. {link}")
        else:
            bot.send_message(message.chat.id, "You haven't sent any YouTube links yet.")
    else:
        bot.send_message(message.chat.id, "You haven't sent any YouTube links yet.")


# Command handler /clear
@bot.message_handler(commands=['clear'])
def handle_clear(message):
    user_id = message.from_user.id
    if user_id in youtube_links:
        youtube_links[user_id] = []
        with open(f"youtube_links_{user_id}.txt", "w") as file:
            file.write("")
        bot.send_message(message.chat.id, "The list of sent links has been cleared.")
    else:
        bot.send_message(message.chat.id, "You don't have any sent links to clear.")


# Helper function to set the user state
def set_user_state(user_id, state):
    USER_STATES[user_id] = state


# Helper function to get the user state
def get_user_state(user_id):
    return USER_STATES.get(user_id, MENU_STATE)


# Helper function to stop playback
def stop_playing(user_id):
    if user_id in playing_status and playing_status[user_id]:
        playing_status[user_id] = False


# Start the bot
bot.polling(none_stop=True)
