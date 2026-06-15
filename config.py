import os
from pymongo import MongoClient

# Permanent Owner ID (Iske liye sab kuch free aur unlimited hai)
OWNER_ID = 8705901135  

API_ID = int(os.environ.get("TELEGRAM_API_ID", 0))
API_HASH = os.environ.get("TELEGRAM_API_HASH", "")
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
SOURCE_CHAT_RAW = os.environ.get("SOURCE_CHAT", "")
MONGO_URL = os.environ.get("MONGO_URL", "") 

def parse_chat_identifier(chat: str) -> str:
    if not chat: return ""
    return str(chat).strip()

SOURCE_CHAT = parse_chat_identifier(SOURCE_CHAT_RAW)

IS_FORWARDER_ACTIVE = True
IS_APPROVAL_ACTIVE = True

SUDO_USERS = []

# Dynamic Global Lists (MongoDB Cloud se sync hongi)
CONNECTED_SESSIONS = []  # List format: [{"session": "...", "name": "..."}]
TARGET_GROUPS = []       # List format: ["@grp1", "@grp2", "-100..."]
APPROVAL_CHATS = []      # Auto-approval channel/group links list

db_collection = None
if MONGO_URL:
    try:
        mongo_client = MongoClient(MONGO_URL)
        db_collection = mongo_client["telegram_bot"]["settings"]
    except Exception as e:
        print(f"❌ MongoDB Connection Error: {e}")

def fetch_cloud_data():
    global CONNECTED_SESSIONS, TARGET_GROUPS, APPROVAL_CHATS, SUDO_USERS
    if db_collection is None: return
    try:
        document = db_collection.find_one({"_id": "bot_configuration"})
        if document:
            CONNECTED_SESSIONS = document.get("sessions", [])
            TARGET_GROUPS = document.get("targets", [])
            APPROVAL_CHATS = document.get("approvals", [])
            SUDO_USERS = document.get("sudo_users", [])
    except Exception as e: pass

def save_cloud_data():
    if db_collection is None: return False
    try:
        db_collection.update_one(
            {"_id": "bot_configuration"},
            {"$set": {
                "sessions": CONNECTED_SESSIONS,
                "targets": TARGET_GROUPS,
                "approvals": APPROVAL_CHATS,
                "sudo_users": SUDO_USERS
            }},
            upsert=True
        )
        return True
    except Exception as e: pass
    return False

# 💳 ECONOMY COUNTERS (Points Database)
def get_user_points(user_id: int) -> int:
    if db_collection is None: return 0
    if user_id == OWNER_ID or user_id in SUDO_USERS: return 99999
    res = db_collection.find_one({"_id": f"user_pts_{user_id}"})
    return res.get("points", 0) if res else 0

def add_user_points(user_id: int, points: int):
    if db_collection is None: return
    current = get_user_points(user_id) if not (user_id == OWNER_ID or user_id in SUDO_USERS) else 0
    db_collection.update_one(
        {"_id": f"user_pts_{user_id}"},
        {"$set": {"points": current + points}},
        upsert=True
    )

def deduct_user_point(user_id: int) -> bool:
    if user_id == OWNER_ID or user_id in SUDO_USERS: return True
    current = get_user_points(user_id)
    if current <= 0: return False
    db_collection.update_one(
        {"_id": f"user_pts_{user_id}"},
        {"$set": {"points": current - 1}},
        upsert=True
    )
    return True

def is_authorized(user_id: int) -> bool:
    return user_id == OWNER_ID or user_id in SUDO_USERS or get_user_points(user_id) > 0

fetch_cloud_data()
      
