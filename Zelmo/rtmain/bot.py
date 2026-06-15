from Zelmo.rtdb import commands
from telethon import TelegramClient

def register_bot_handlers(bot_client: TelegramClient, user_clients, loop):
    commands.register_all_commands(bot_client, user_clients, loop)
