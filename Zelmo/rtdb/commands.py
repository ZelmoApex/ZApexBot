import config
import asyncio
import random
import re
from Zelmo.rtdb import userbot, messages, buttons
from Zelmo.utils import get_secure_entity
from telethon import TelegramClient, events, errors
from telethon.sessions import StringSession
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.tl.functions.messages import ImportChatInviteRequest

def extract_link_data(link_str):
    link_str = link_str.strip()
    if not link_str: return None
    if "joinchat/" in link_str or "t.me/+" in link_str:
        return {"type": "private", "data": link_str.split('/')[-1].replace('+', '')}
    else:
        username = link_str.split('/')[-1].replace('@', '')
        return {"type": "public", "data": username}

async def add_new_user_client(session_str, event, user_clients, loop):
    status_msg = await event.respond("⏳ Account connect aur verify ho raha hai...")
    try:
        u_client = TelegramClient(StringSession(session_str), config.API_ID, config.API_HASH)
        await u_client.connect()
        if not await u_client.is_user_authorized():
            return await status_msg.edit("❌ Error: String Session invalid hai!")
        
        me = await u_client.get_me()
        name_display = f"{me.first_name} (@{me.username or 'NoUser'})"
        
        config.CONNECTED_SESSIONS.append({"session": session_str, "name": name_display})
        config.save_cloud_data()
        
        session_idx = len(config.CONNECTED_SESSIONS) - 1
        user_clients[session_idx] = u_client
        userbot.setup_live_forwarder(u_client)
        
        loop.create_task(u_client.run_until_disconnected())
        await status_msg.edit(f"✅ **Account Connected Successfully!**\nAdded as ID #{session_idx + 1}: {name_display}")
    except Exception as e:
        await status_msg.edit(f"❌ Connection Error: {e}")

def register_all_commands(bot_client: TelegramClient, user_clients, loop):

    @bot_client.on(events.NewMessage(pattern='/start'))
    async def start_handler(event):
        sender = event.sender_id
        # Strict Owner check for Admin Panel
        if sender == config.OWNER_ID or sender in config.SUDO_USERS:
            await event.respond(messages.START_TITLE, buttons=buttons.get_dashboard_buttons())
        elif config.get_user_points(sender) > 0:
            await event.respond("🚀 **Welcome back!**\nAapka balance active hai. Use `/brod <message>` to broadcast.")
        else:
            await event.respond(messages.get_premium_pitch(sender), buttons=buttons.get_premium_buttons())

    @bot_client.on(events.NewMessage(pattern='/help'))
    async def help_handler(event):
        sender = event.sender_id
        if not config.is_authorized(sender):
            return await event.respond(messages.get_premium_pitch(sender), buttons=buttons.get_premium_buttons())
        await event.respond(messages.HELP_TEXT)
        if sender == config.OWNER_ID or sender in config.SUDO_USERS:
            await event.respond(messages.OWNER_HELP_TEXT)

    @bot_client.on(events.NewMessage(pattern='/status'))
    async def status_handler(event):
        sender = event.sender_id
        if not config.is_authorized(sender):
            return await event.respond(messages.get_premium_pitch(sender), buttons=buttons.get_premium_buttons())
        await event.respond(messages.format_status_text(sender))

    @bot_client.on(events.CallbackQuery())
    async def callback_handler(event):
        sender = event.sender_id
        if event.data == b"check_status":
            if sender == config.OWNER_ID or sender in config.SUDO_USERS:
                return await event.edit(messages.format_status_text(sender), buttons=buttons.get_dashboard_buttons())
            elif config.get_user_points(sender) > 0:
                return await event.answer(f"💰 Balance: {config.get_user_points(sender)} Points", alert=True)
            else:
                return await event.edit(messages.get_premium_pitch(sender), buttons=buttons.get_premium_buttons())
                
        if sender != config.OWNER_ID and sender not in config.SUDO_USERS:
            return await event.answer("🚫 Staff access required.", alert=True)
            
        if event.data == b"f_on": config.IS_FORWARDER_ACTIVE = True
        elif event.data == b"f_off": config.IS_FORWARDER_ACTIVE = False
        elif event.data == b"a_on": config.IS_APPROVAL_ACTIVE = True
        elif event.data == b"a_off": config.IS_APPROVAL_ACTIVE = False
            
        await event.edit(messages.format_status_text(sender), buttons=buttons.get_dashboard_buttons())

    @bot_client.on(events.NewMessage())
    async def text_commands(event):
        text = event.raw_text.strip()
        sender = event.sender_id
        
        # 🔥 MULTI-ID PAID BROADCASTER EXECUTION
        if text.startswith("/brod "):
            promo_msg = text.replace("/brod ", "").strip()
            if not promo_msg:
                return await event.respond("❌ Please type a message!")
                
            if not config.deduct_user_point(sender):
                return await event.respond(messages.get_premium_pitch(sender), buttons=buttons.get_premium_buttons())
                
            progress = await event.respond("⏳ Processing broadcast through all connected IDs...")
            sent_count = 0
            if not user_clients:
                return await progress.edit("❌ System Error: No active IDs connected.")
            if not config.TARGET_GROUPS:
                return await progress.edit("❌ System Error: Target groups list is empty.")

            for client_idx, client in user_clients.items():
                for target in config.TARGET_GROUPS:
                    try:
                        peer = await get_secure_entity(client, target)
                        await client.send_message(peer, promo_msg)
                        sent_count += 1
                    except Exception: pass
                    await asyncio.sleep(random.uniform(1.0, 2.5))
                        
            await progress.edit(f"✅ **Broadcast Done!** Total Sent: `{sent_count}` destinations.")
            return

        # 🛑 SECURITY: STRICT OWNER/SUDO VALIDATION
        if sender != config.OWNER_ID and sender not in config.SUDO_USERS:
            return

        # FIXED DYNAMIC POINTS ADDER WITH LIVE FORCE WRITE
        if text.startswith("/add_points"):
            try:
                parts = text.split()
                if len(parts) < 3:
                    return await event.respond("❌ Format: `/add_points <user_id> <points>`")
                
                target_user = int(parts[1])
                pts_to_add = int(parts[2])
                
                config.add_user_points(target_user, pts_to_add)
                verified_pts = config.get_user_points(target_user)
                
                await event.respond(f"✅ **Points Loaded Successfully!**\n👤 User ID: `{target_user}`\n📊 Total Current Balance: `{verified_pts} Points`")
                try:
                    await bot_client.send_message(target_user, f"🎉 **Points Loaded!**\n💰 Admin ne aapke account me `{pts_to_add}` points load kar diye hain. Use `/brod <message>` now!")
                except Exception: pass
            except ValueError:
                await event.respond("❌ Numerical digits required for ID & points.")
            except Exception as e:
                await event.respond(f"❌ DB Write Error: {e}")
            return

        elif text.startswith("/check_points"):
            try:
                target_user = int(text.replace("/check_points", "").strip())
                await event.respond(f"👤 User `{target_user}` has `{config.get_user_points(target_user)}` points.")
            except Exception: pass
            return

        elif text.startswith("/add_sudo") or text.startswith("/del_sudo"):
            try:
                target_sudo = int(text.split()[1])
                if text.startswith("/add_sudo") and target_sudo not in config.SUDO_USERS:
                    config.SUDO_USERS.append(target_sudo); config.save_cloud_data(); await event.respond("✅ Added Sudo.")
                elif text.startswith("/del_sudo") and target_sudo in config.SUDO_USERS:
                    config.SUDO_USERS.remove(target_sudo); config.save_cloud_data(); await event.respond("🗑️ Removed Sudo.")
            except Exception: pass
            return

        if text.startswith("/add_id "):
            session = text.replace("/add_id ", "").strip()
            if session: await add_new_user_client(session, event, user_clients, loop)
            
        elif text.startswith("/add_group "):
            args = text.replace("/add_group ", "").strip()
            if args:
                new_groups = [config.parse_chat_identifier(g) for g in args.split(",") if g.strip()]
                for g in new_groups:
                    if g not in config.TARGET_GROUPS: config.TARGET_GROUPS.append(g)
                config.save_cloud_data()
                await event.respond(f"✅ Target groups updated! Total: `{len(config.TARGET_GROUPS)}` groups.")
                
        elif text.startswith("/add_approve "):
            arg = text.replace("/add_approve ", "").strip()
            if arg:
                if arg not in config.APPROVAL_CHATS: config.APPROVAL_CHATS.append(config.parse_chat_identifier(arg))
                config.save_cloud_data()
                await event.respond(f"✅ Approval link updated!")

        # Distributed Joiner Command 
        elif text.startswith("/join_all "):
            raw_links = text.replace("/join_all ", "").strip()
            links_list = [l.strip() for l in re.split(r'[,\n]', raw_links) if l.strip()]
            
            if not user_clients:
                return await event.respond("❌ Bot me koi active ID nahi hai!")
            if not links_list:
                return await event.respond("❌ Links list khali hai!")
                
            total_ids = len(user_clients)
            total_links = len(links_list)
            
            progress = await event.respond(
                f"🤖 **Smart Distributed Joiner Started!**\n"
                f"📋 Total Links: `{total_links}` | 👤 Active IDs: `{total_ids}`\n\n"
                f"🛡️ **Anti-Ban Shield Active!**"
            )

            client_keys = list(user_clients.keys())
            reports_summary = []

            for rank, key_idx in enumerate(client_keys):
                client = user_clients[key_idx]
                me = await client.get_me()
                client_name = me.first_name
                
                start_slice = int((rank / total_ids) * total_links)
                end_slice = int(((rank + 1) / total_ids) * total_links)
                my_assigned_links = links_list[start_slice:end_slice]
                
                if not my_assigned_links: continue
                    
                await bot_client.send_message(sender, f"⏳ **ID {rank+1}/{total_ids} [{client_name}]** ne kaam shuru kiya...")
                
                success_join = 0
                request_sent = 0
                failed_count = 0
                
                for link in my_assigned_links:
                    link_info = extract_link_data(link)
                    if not link_info: continue
                    
                    try:
                        if link_info["type"] == "private":
                            try:
                                await client(ImportChatInviteRequest(link_info["data"]))
                                success_join += 1
                            except errors.FloodWaitError as f:
                                await bot_client.send_message(sender, f"⚠️ FloodWait on {client_name}. Sleeping for {f.seconds}s.")
                                await asyncio.sleep(f.seconds)
                            except errors.UserAlreadyParticipantError:
                                success_join += 1
                            except Exception as e:
                                if "request" in str(e).lower() or "join" in str(e).lower(): request_sent += 1
                                else: failed_count += 1
                        else:
                            try:
                                await client(JoinChannelRequest(link_info["data"]))
                                success_join += 1
                            except errors.FloodWaitError as f:
                                await asyncio.sleep(f.seconds)
                            except Exception as e:
                                if "request" in str(e).lower(): request_sent += 1
                                else: failed_count += 1
                    except Exception:
                        failed_count += 1
                        
                    await asyncio.sleep(random.uniform(15.0, 35.0))
                
                id_report = f"👤 **ID:** {client_name}\n🟢 Joined: `{success_join}` | 📩 Request Sent: `{request_sent}` | ❌ Failed: `{failed_count}`"
                await bot_client.send_message(sender, f"📊 **ID Task Done!**\n{id_report}")
                reports_summary.append(id_report)
                await asyncio.sleep(5)

            final_report_text = "🏁 **Auto-Joiner Engine Work Completed!**\n\n**🎯 FINAL SUMMARY REPORT:**\n\n" + "\n\n".join(reports_summary)
            await progress.edit(final_report_text)
            return

        elif text == "/clear_all":
            for cl in user_clients.values():
                try: await cl.disconnect()
                except Exception: pass
            user_clients.clear()
            config.CONNECTED_SESSIONS = []
            config.TARGET_GROUPS = []
            config.APPROVAL_CHATS = []
            config.save_cloud_data()
            await event.respond(messages.RESET_SUCCESS)
        
