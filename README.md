# Camera-Enhanced Telegram Bot

## Description
This project uses a Telegram bot that interacts with video data through a connected camera. It has the capabilities to capture, process and stream video data, as well as download videos from YouTube, followed by the inclusion of a file.

## Features
- **Video Capture & Processing:** Utilizes `pygame.camera` for handling video operations.
- **Video Streaming:** Streams video data efficiently.
- **YouTube Downloads:** Integrates `pytube` for downloading videos directly through the bot.
- **Play downloaded youtube mp3/mp4 files

## Requirements
- Python 3.x
- `telebot`
- `pygame`
- `pytube`
- Additional dependencies are listed in `requirements.txt`.

## Setup
1. **Clone the repository:**
   ```bash
   git clone https://github.com/ToxicSnail/dorm_bot.git
   cd dorm_bot.git
2. **Install the necessary Python packages:
   ```bash
   pip install -r requirements.txt

## Usage
1. **Encrypt your password:**
   Before launching the bot, you must first encrypt a password that will be used for bot access:
   ```bash
   python encryptor.py
   'Follow the prompts to enter and encrypt the password. The encrypted password will be saved in secret.txt.'
1. **Configure your Telegram API token:**
   Ensure you have a valid Telegram API token and save it in a file named api.txt.
4. **Run the bot:**
   ```bash
   python dorm.py
5. **Interact with the bot on Telegram to access its functionalities.**

## Configuration
- The bot uses a camera connected through /dev/video0 with a resolution of 640x426 pixels.
- Videos are processed and streamed in the specified format and quality.

## License
This is project open-sourse.
I developted this in my course work in University
@Gorky Kirill
