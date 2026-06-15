#!/usr/bin/env python3
import asyncio
import sys
import os
from flask import Flask
from threading import Thread

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import config
from Zelmo.rtmain import bot
from Zelmo.rtdb import userbot
from telethon import TelegramClient
from telethon.sessions import StringSession

# 🌐 Dummy Web Server to bypass Render Web Service port check
app = Flask('')

@app.route('/')
def home():
    return "Bot is running 24/7 on Free Instance!"

def run_flask():
    # Render automatic PORT env variable deta hai, default 10000 use hoga
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

async def main():
    loop = asyncio.get_running_loop()
    user_clients = {} 
    
    bot_client = TelegramClient('bot_controller', config.API_ID, config.API_HASH)
    bot.register_bot_handlers(bot_client, user_clients, loop)
    await bot_client.start(bot_token=config.BOT_TOKEN)
    
    # Auto-load dynamic sessions from database on startup
    if config.CONNECTED_SESSIONS:
        for idx, item in enumerate(config.CONNECTED_SESSIONS):
            try:
                u_cl = TelegramClient(StringSession(item["session"]), config.API_ID, config.API_HASH)
                await u_cl.connect()
                if await u_cl.is_user_authorized():
                    user_clients[idx] = u_cl
                    userbot.setup_live_forwarder(u_cl)
                    loop.create_task(u_cl.run_until_disconnected())
            except Exception: pass

    asyncio.create_task(userbot.old_requests_cleaner(user_clients))
    
    print(f"🚀 Master Multi-ID Engine Online on Web Service! Active IDs: {len(user_clients)}")
    await bot_client.run_until_disconnected()

if __name__ == "__main__":
    # 🧵 Flask server ko alag thread me start karenge taaki port check pass ho jaye
    Thread(target=run_flask).start()
    # 🤖 Main Telegram Bot engine run karenge
    asyncio.run(main())
    
