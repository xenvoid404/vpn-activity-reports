#!/usr/bin/env python3
"""
Test script untuk userbot - gunakan ini untuk debugging
"""

import asyncio
import os
import logging
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError, ApiIdInvalidError, PhoneCodeInvalidError

# Setup logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_connection():
    """Test koneksi ke Telegram"""
    
    # Ambil credentials
    api_id = int(os.getenv('API_ID', '25329914'))
    api_hash = os.getenv('API_HASH', '319773b99dd80f1a76de582aa0d478e4')
    session_name = os.getenv('SESSION_NAME', 'userbot')
    
    logger.info(f"Testing connection with API_ID: {api_id}")
    logger.info(f"Session file: {session_name}.session")
    
    client = TelegramClient(session_name, api_id, api_hash)
    
    try:
        logger.info("Connecting to Telegram...")
        await client.start()
        
        # Get user info
        me = await client.get_me()
        logger.info(f"✅ Successfully connected as: {me.first_name} (@{me.username})")
        logger.info(f"User ID: {me.id}")
        
        # Test target group access
        target_group = int(os.getenv('TARGET_GROUP', '-1002537991702'))
        try:
            entity = await client.get_entity(target_group)
            logger.info(f"✅ Can access target group: {entity.title}")
        except Exception as e:
            logger.error(f"❌ Cannot access target group {target_group}: {e}")
        
        # List recent dialogs
        logger.info("\n📱 Recent chats:")
        async for dialog in client.iter_dialogs(limit=5):
            logger.info(f"  - {dialog.name} (ID: {dialog.id})")
        
        return True
        
    except ApiIdInvalidError:
        logger.error("❌ API ID atau Hash tidak valid!")
        return False
    except SessionPasswordNeededError:
        logger.error("❌ Akun memerlukan 2FA password!")
        return False
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        return False
    finally:
        await client.disconnect()

async def main():
    logger.info("🔍 Testing userbot connection...")
    
    # Check session file exists
    session_file = f"{os.getenv('SESSION_NAME', 'userbot')}.session"
    if os.path.exists(session_file):
        logger.info(f"✅ Session file found: {session_file}")
        file_size = os.path.getsize(session_file)
        logger.info(f"Session file size: {file_size} bytes")
        
        if file_size < 100:
            logger.warning("⚠️ Session file seems too small, might be corrupted")
    else:
        logger.warning(f"⚠️ Session file not found: {session_file}")
        logger.info("You'll need to authenticate when running for the first time")
    
    success = await test_connection()
    
    if success:
        logger.info("✅ All tests passed! Userbot should work fine.")
    else:
        logger.error("❌ Tests failed! Check the errors above.")

if __name__ == "__main__":
    asyncio.run(main())