Telegram Backup Bot
This Telegram bot allows you to create backups of files sent to it. The bot can save files locally and upload them to Yandex.Disk and Google Drive.

Installation
Install the required packages by running the following command:
pip install -r requirements.txt
Obtain the necessary API tokens and credentials:

Telegram bot token:

Create a new bot on Telegram by following the instructions on the official Telegram Bot API page.
Obtain the API token for your bot.
Save the API token in a file named TGtoken.txt. Each bot should have its own unique token.
Yandex.Disk token:

Go to the Yandex Developer Console and sign in.
Create a new application and obtain an access token for the Yandex.Disk API.
Save the token in a file named YDtoken.txt.
Google Drive credentials:

Go to the Google Developer Console and sign in.
Create a new project or select an existing one.
Enable the Google Drive API for your project.
Create OAuth 2.0 credentials and download the JSON file with client secrets.
Save the JSON file with client secrets as client_secrets.json.
Create a folder named backup in the same directory as the script. This folder will be used to store the backup files.

Usage
Run the bot by executing the script:

Send the /start command to the bot on Telegram to initiate the backup process.

Upon request, send the files you want to back up. You can send multiple files at once. Make sure to send files even if they are photos or other multimedia objects. When sending from a phone, use the file attachment feature.

After sending all the files, you will be prompted to upload them to Yandex.Disk. Reply with "Yes" or "No".

You will then be prompted to upload the files to Google Drive. Reply with "Yes" or "No".

After uploading the files to Yandex.Disk and/or Google Drive, you will be given the option to continue the backup process or return to the menu.
