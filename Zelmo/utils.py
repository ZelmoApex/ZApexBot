from telethon.tl.functions.messages import ImportChatInviteRequest
from telethon import errors

async def get_secure_entity(client, target_str):
    if not target_str: return None
    target_str = str(target_str).strip()
    
    if target_str.startswith('-') and target_str[1:].isdigit(): return int(target_str)
    if target_str.isdigit(): return int(target_str)
        
    if "t.me/+" in target_str or "t.me/joinchat/" in target_str:
        invite_hash = target_str.split('/')[-1].replace('+', '')
        try:
            updates = await client(ImportChatInviteRequest(invite_hash))
            return updates.chats[0].id
        except errors.UserAlreadyParticipantError:
            return target_str
        except Exception:
            return target_str
            
    return target_str
