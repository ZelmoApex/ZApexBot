from telethon import Button
import config

def get_dashboard_buttons():
    return [
        [Button.inline("📡 Forwarder ON", b"f_on"), Button.inline("📡 Forwarder OFF", b"f_off")],
        [Button.inline("⚡ Approver ON", b"a_on"), Button.inline("⚡ Approver OFF", b"a_off")],
        [Button.inline("📊 Check Status Details", b"check_status")]
    ]

def get_premium_buttons():
    owner_link = f"tg://user?id={config.OWNER_ID}"
    return [
        [Button.url("💳 Buy Points (₹200 = 3 Points)", owner_link)],
        [Button.inline("🔄 Refresh Balance", b"check_status")]
    ]
