import asyncio
import random
import config
from Zelmo.utils import get_secure_entity
from telethon import events
from telethon.tl.functions.messages import HideChatJoinRequestRequest
from telethon.tl.types import MessageService

async def old_requests_cleaner(user_clients):
    await asyncio.sleep(15)
    while True:
        if config.IS_APPROVAL_ACTIVE and config.APPROVAL_CHATS:
            for client_idx, client in user_clients.items():
                for target in config.APPROVAL_CHATS:
                    try:
                        resolved_peer = await get_secure_entity(client, target)
                        async for request in client.iter_chat_join_requests(resolved_peer):
                            if not config.IS_APPROVAL_ACTIVE: break
                            try:
                                await client(HideChatJoinRequestRequest(
                                    peer=resolved_peer, user_id=request.user_id, approve=True
                                ))
                                await asyncio.sleep(random.uniform(1.5, 3.0)) 
                            except Exception: pass
                    except Exception: pass
        await asyncio.sleep(60)

def setup_live_forwarder(client):
    @client.on(events.NewMessage(chats=config.SOURCE_CHAT))
    async def forward_handler(ev):
        if not config.IS_FORWARDER_ACTIVE or isinstance(ev.message, MessageService): return
        if not config.TARGET_GROUPS: return
        for target in config.TARGET_GROUPS:
            try:
                peer = await get_secure_entity(ev.client, target)
                await asyncio.sleep(random.uniform(2, 5))
                await ev.client.send_message(peer, ev.message)
            except Exception: pass
