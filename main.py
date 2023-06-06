import os
import requests
import uuid
import telebot
from telebot import types
import logging
from datetime import datetime
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import yadisk

TG_TOKEN_FILE = 'TGtoken.txt'
YD_TOKEN_FILE = 'YDtoken.txt'
FOLDER_NAME = 'backup'

# Create the 'backup' folder if it doesn't exist
if not os.path.exists('backup'):
    os.makedirs('backup')

folder_path = os.path.join(os.getcwd(), FOLDER_NAME, datetime.now().strftime('%Y-%m-%d'))

# Create a folder with the current date if it doesn't exist
if not os.path.exists(folder_path):
    os.makedirs(folder_path)

if not os.access(folder_path, os.W_OK):
    logging.warning("Bot does not have write access to the backup folder.")
else:
    logging.info("Bot has write access to the backup folder.")

def get_token(file_path):
    with open(file_path, 'r') as file:
        token = file.read().strip()
        return token

def upload_files_to_yandex_disk(folder_path, token):
    y = yadisk.YaDisk(token=token)
    y.mkdir(folder_path)
    for file_name in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file_name)
        y.upload(file_path, f"{folder_path}/{file_name}")

def upload_files_to_google_drive(folder_path):
    gauth = GoogleAuth()
    gauth.LoadClientConfigFile('client_secrets.json')
    gauth.LocalWebserverAuth()
    drive = GoogleDrive(gauth)
    for file_name in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file_name)
        gfile = drive.CreateFile({'title': file_name})
        gfile.SetContentFile(file_path)
        gfile.Upload()

# Start the bot
bot = telebot.TeleBot(get_token(TG_TOKEN_FILE))

# Logging configuration
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

@bot.message_handler(commands=['start'])
def send_welcome(message):
    logging.debug("Received /start command")
    bot_token = get_token(TG_TOKEN_FILE)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton('Send files to backup'))
    markup.add(types.KeyboardButton('Menu'))
    bot.reply_to(message, "Hello, traveler! What would you like to do?", reply_markup=markup)
    logging.info("Bot started")

@bot.message_handler(func=lambda message: message.text == 'Send files to backup')
def ask_for_files(message):
    logging.debug("Received 'Send files to backup' command")
    bot.reply_to(message, "Please send me the files to save.")
    bot.register_next_step_handler(message, save_files)

def save_files(message):
    logging.debug("Received files")
    if message.document:
        file_ids = []
        file_ids.append(message.document.file_id)
        bot.reply_to(message, "Please send me more files or press the 'done' button to finish.", reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True).add(types.KeyboardButton('done')))
        bot.register_next_step_handler(message, process_files, file_ids)
    else:
        bot.reply_to(message, "No file found in the message.")
        logging.warning("No file found in the message.")

def process_files(message, file_ids):
    if message.text == 'done':
        for file_id in file_ids:
            file_info = bot.get_file(file_id)
            file_path = file_info.file_path
            file_name = file_path.split('/')[-1]
            file_unique_id = str(uuid.uuid4())
            backup_path = os.path.join(folder_path, f"{file_unique_id}_{file_name}")
            file_url = f"https://api.telegram.org/file/bot{get_token(TG_TOKEN_FILE)}/{file_path}"
            response = requests.get(file_url)
            with open(backup_path, 'wb') as file:
                file.write(response.content)
        bot.reply_to(message, "All files saved successfully.")
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(types.KeyboardButton('Yes'))
        markup.add(types.KeyboardButton('No'))
        bot.reply_to(message, "Would you like to upload the files to Yandex.Disk?", reply_markup=markup)
        bot.register_next_step_handler(message, upload_to_yandex_disk)
    else:
        file_ids.append(message.document.file_id)
        bot.reply_to(message, "Please send me more files or press the 'done' button to finish.", reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True).add(types.KeyboardButton('done')))
        bot.register_next_step_handler(message, process_files, file_ids)

def upload_to_yandex_disk(message):
    if message.text.lower() == 'yes':
        try:
            token = get_token(YD_TOKEN_FILE)
            upload_files_to_yandex_disk(folder_path, token)
            logging.info("Files successfully uploaded to Yandex.Disk.")
            bot.reply_to(message, "Files successfully uploaded to Yandex.Disk.")
        except Exception as e:
            logging.error(f"Error uploading files to Yandex.Disk: {e}")
            bot.reply_to(message, "Error uploading files to Yandex.Disk.")
    else:
        logging.info("User chose not to upload files to Yandex.Disk.")
        bot.reply_to(message, "Files were not uploaded to Yandex.Disk.")

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton('Yes'))
    markup.add(types.KeyboardButton('No'))
    bot.reply_to(message, "Would you like to upload the files to Google Drive?", reply_markup=markup)
    bot.register_next_step_handler(message, upload_to_google_drive)

def upload_to_google_drive(message):
    if message.text.lower() == 'yes':
        try:
            upload_files_to_google_drive(folder_path)
            logging.info("Files successfully uploaded to Google Drive.")
            bot.reply_to(message, "Files successfully uploaded to Google Drive.")
        except Exception as e:
            logging.error(f"Error uploading files to Google Drive: {e}")
            bot.reply_to(message, "Error uploading files to Google Drive.")
    else:
        logging.info("User chose not to upload files to Google Drive.")
        bot.reply_to(message, "Files were not uploaded to Google Drive.")

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton('Send files to backup'))
    markup.add(types.KeyboardButton('Menu'))
    bot.reply_to(message, "What would you like to do next?", reply_markup=markup)

bot.polling()


