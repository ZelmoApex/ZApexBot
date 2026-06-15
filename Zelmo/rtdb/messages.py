import config

HELP_TEXT = (
    "🚀 **Unlimited Dynamic Paid Broadcast Bot** 🚀\n\n"
    "📝 **Normal User Command:**\n"
    "• `/brod <Aapka Message>` ➔ Bot me connected sabhi IDs se saare target groups me ek sath message bhejta hai.\n"
    "💰 **Cost:** 1 Point per broadcast request."
)

OWNER_HELP_TEXT = (
    "👑 **ADMIN UNLIMITED CONTROL PANEL:**\n\n"
    "⚙️ **Dynamic Infrastructure Setup:**\n"
    "• `/add_id <session>` ➔ Ek aur naya account connect karein (Unlimited IDs allowed)\n"
    "• `/add_group @username` ➔ Ek naya target group jodein\n"
    "• `/add_approve <link>` ➔ Naya auto-approval link jodein\n\n"
    "🤖 **SMART DISTRIBUTED JOINER (Anti-Ban):**\n"
    "• `/join_all <links>` ➔ Saari IDs me groups ko barabar baant kar (distribute) join karwaye.\n"
    "  *Example:* `/join_all link1, link2, link3`\n\n"
    "📊 **System Status & Reset:**\n"
    "• `/status` ➔ Saari details aur live ID reports dekhein\n"
    "• `/clear_all` ➔ Poora database clear aur sessions disconnect karein\n\n"
    "💳 **User Points Control:**\n"
    "• `/add_points <user_id> <amount>` ➔ Normal user ko points dein\n"
    "• `/check_points <user_id>` ➔ User balance check karein\n"
    "• `/add_sudo <user_id>` | `/del_sudo <user_id>`"
)

START_TITLE = "⚙️ **Dynamic Control Panel Loaded** ⚙️"
RESET_SUCCESS = "🗑️ Sabhi accounts aur groups database se clear kar diye gaye hain."

def get_premium_pitch(user_id: int):
    return (
        "🚫 **Aapka Points Balance 0 Hai!**\n\n"
        "✨ Is bot se promotion broadcast karne ke liye points buy karne honge.\n"
        "💰 **Offer:** ₹200 mein 3 Points milenge.\n"
        "🎯 **Rule:** 1 Point = 1 `/brod` execution shot.\n\n"
        f"👤 **Your Telegram ID:** `{user_id}`\n"
        "👇 Niche diye gaye button par click karke Admin se points load karwayein!"
    )

def format_status_text(user_id: int):
    f_status = "🟢 ON" if config.IS_FORWARDER_ACTIVE else "🔴 OFF"
    a_status = "🟢 ON" if config.IS_APPROVAL_ACTIVE else "🔴 OFF"
    
    user_pts = config.get_user_points(user_id)
    pts_display = "♾️ Unlimited (Staff)" if (user_id == config.OWNER_ID or user_id in config.SUDO_USERS) else f"{user_pts} Points"
    
    id_list_str = ""
    if config.CONNECTED_SESSIONS:
        for idx, s in enumerate(config.CONNECTED_SESSIONS, 1):
            id_list_str += f"{idx}. {s['name']}\n"
    else:
        id_list_str = "[Koi account connected nahi hai]\n"
        
    return (
        f"🤖 **Bot Dynamic Live Dashboard**\n"
        f"-----------------------------------\n"
        f"💰 **Aapka Balance:** `{pts_display}`\n"
        f"📡 Live Forwarder: {f_status} | ⚡ Auto-Approver: {a_status}\n\n"
        f"📊 **Total Accounts Connected:** `{len(config.CONNECTED_SESSIONS)} IDs`\n"
        f"👥 **Total Target Groups Added:** `{len(config.TARGET_GROUPS)} Groups`\n"
        f"🔐 **Total Auto-Approval Chats:** `{len(config.APPROVAL_CHATS)} Links`\n\n"
        f"📝 **Connected Active IDs:**\n{id_list_str}"
    )
