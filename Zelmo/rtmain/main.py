#!/usr/bin/env python3
import asyncio
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import config
from Zelmo.rtmain import bot
from Zelmo.rtdb import userbot
from telethon import TelegramClient
from telethon.sessions import StringSession

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
    
    print(f"🚀 Master Multi-ID Engine Online! Active IDs: {len(user_clients)}")
    await bot_client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
