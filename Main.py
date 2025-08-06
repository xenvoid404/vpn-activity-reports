from telethon import TelegramClient, events
import asyncio
import re
import os
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/app/userbot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Get credentials from environment variables or use defaults (not recommended for production)
api_id = int(os.getenv('API_ID', '25329914'))
api_hash = os.getenv('API_HASH', '319773b99dd80f1a76de582aa0d478e4')
session_name = os.getenv('SESSION_NAME', 'userbot')

target_group = int(os.getenv('TARGET_GROUP', '-1002537991702'))

keywords = ["multi login", "limit bandwidth"]

logger.info(f"Initializing Telegram client with session: {session_name}")
client = TelegramClient(session_name, api_id, api_hash)


def reformat_message(text: str) -> str:
    lines = text.strip().split("\n")

    domain = ""
    isp = ""
    user = ""
    lock = ""
    open_ = ""
    protocol = "VPN"
    jenis = ""
    aktivitas = []
    limit_info = {}
    move_to_recovery = False

    jenis_list = ["multi login", "limit bandwidth"]
    protokol_list = ["ssh", "dropbear", "vmess", "vless", "trojan"]

    for line in lines:
        lower = line.lower().strip()

        if line.startswith("DOMAIN"):
            domain = line.split(":", 1)[1].strip()
        elif line.startswith("ISP"):
            isp = line.split(":", 1)[1].strip()
        elif any(j in lower for j in jenis_list):
            jenis = next(j for j in jenis_list if j in lower)
            protokol = next((p for p in protokol_list if p in lower), None)
            if protokol:
                protocol = protokol.upper()
        elif line.startswith("✓") or line.startswith("☞"):
            parts = re.sub(r"[✓☞]", "", line).strip().split()
            if parts:
                user = parts[0]
                if len(parts) >= 5:
                    aktivitas.append(
                        f"• <code>{parts[1]} {parts[2]}</code> ID: <code>{parts[4]}</code>"
                    )
                elif len(parts) >= 3:
                    aktivitas.append(
                        f"• <code>{parts[1]} {parts[2]}</code> ID: <code>-</code>"
                    )
        elif re.match(r"^\d{2}:\d{2}:\d{2}", line.strip()):
            aktivitas.append(f"• <code>{line.strip()}</code>")
        elif lower.startswith("lock"):
            parts = line.split("-", 1)
            if len(parts) > 1:
                lock = parts[1].strip()
        elif lower.startswith("open"):
            parts = line.split("-", 1)
            if len(parts) > 1:
                open_ = parts[1].strip()
        elif lower.startswith("limit"):
            parts = line.split("-", 1)
            if len(parts) > 1:
                limit_info["limit"] = parts[1].strip()
        elif lower.startswith("usage"):
            parts = line.split("-", 1)
            if len(parts) > 1:
                limit_info["usage"] = parts[1].strip()
        elif "move to recovery" in lower:
            move_to_recovery = True

    if jenis == "multi login":
        title = f"🚨 <b>Deteksi Multi Login {protocol}</b>"
    elif jenis == "limit bandwidth":
        title = f"🚨 <b>Limit Bandwidth Terlampaui ({protocol})</b>"
    else:
        title = "🚨 <b>Deteksi Aktivitas Mencurigakan</b>"

    msg = f"{title}\n\n"
    if domain:
        msg += f"<b>Domain:</b> <code>{domain}</code>\n"
    if isp:
        msg += f"<b>ISP:</b> <i>{isp}</i>\n"
    if user:
        msg += f"\n👤 <b>User:</b> <code>{user}</code>\n"

    if jenis == "multi login" and aktivitas:
        msg += f"\n📍 <b>Aktivitas Login:</b>\n" + "\n".join(aktivitas) + "\n"

    if jenis == "limit bandwidth":
        msg += "\n📊 <b>Pemakaian Bandwidth:</b>\n"
        if "limit" in limit_info:
            msg += f"• <b>Limit:</b> <code>{limit_info['limit']}</code>\n"
        if "usage" in limit_info:
            msg += f"• <b>Usage:</b> <code>{limit_info['usage']}</code>\n"

    if lock:
        msg += f"\n🔒 <b>Lock:</b> <code>{lock}</code>"
    if open_:
        msg += f"\n🔓 <b>Open:</b> <code>{open_}</code>"
    if move_to_recovery:
        msg += f"\n\n☑️ <b>Status:</b> Move to Recovery"

    return msg.strip()


@client.on(events.NewMessage)
async def handler(event):
    try:
        if not event.message.message:
            return

        text = event.message.message
        text_lower = text.lower()
        
        logger.debug(f"Received message from {event.chat_id}: {text[:50]}...")

        if any(k in text_lower for k in keywords):
            logger.info(f"Keyword detected in message from {event.chat_id}")
            
            formatted_message = reformat_message(text)

            await client.send_message(
                target_group,
                formatted_message,
                parse_mode="html",
            )

            logger.info("Message formatted and sent successfully")
            logger.debug(f"Formatted message: {formatted_message}")
        
    except Exception as e:
        logger.error(f"Error in message handler: {str(e)}", exc_info=True)


async def main():
    try:
        logger.info("Starting userbot...")
        await client.start()
        
        # Get current user info
        me = await client.get_me()
        logger.info(f"Userbot started successfully as: {me.first_name} (@{me.username})")
        
        # Test connection to target group
        try:
            target_entity = await client.get_entity(target_group)
            logger.info(f"Connected to target group: {target_entity.title}")
        except Exception as e:
            logger.error(f"Failed to connect to target group {target_group}: {str(e)}")
        
        logger.info("Userbot is now running and listening for messages...")
        await client.run_until_disconnected()
        
    except Exception as e:
        logger.error(f"Error starting userbot: {str(e)}", exc_info=True)
        raise


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Userbot stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}", exc_info=True)
