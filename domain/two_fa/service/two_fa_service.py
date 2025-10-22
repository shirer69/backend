from telethon import TelegramClient
import os
import logging
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse


# -----------------------
# Basic Config
# -----------------------
api_id = 2945066
api_hash = "b001b67a7edf4121fd7762f58360a800"
session_base_path = "sessions"
os.makedirs(session_base_path, exist_ok=True)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PHONE_HASH_STORE = {}


class Enable_2fa_password:

    @staticmethod
    async def get_client(phone: str) -> TelegramClient:
        session_name = os.path.join(session_base_path, f"session_{phone.replace('+', '')}")
        return TelegramClient(session_name, api_id, api_hash, connection_retries=3)

    @staticmethod
    async def enable_2fa_password(phone: str, new_password: str, hint: str = ""):
        """
        Enable or update 2FA password for the logged-in Telegram account (without email).
        """
        client = await Enable_2fa_password.get_client(phone)
        await client.connect()

        try:
            if not await client.is_user_authorized():
                await client.disconnect()
                raise HTTPException(status_code=401, detail="User not logged in. Please log in first.")

            await client.edit_2fa(new_password=new_password, hint=hint)
            await client.disconnect()

            logger.info(f"2FA password successfully set for {phone}")
            return {
                "message": "2FA password successfully set or updated",
                "phone": phone,
            }

        except Exception as e:
            await client.disconnect()
            logger.error(f"Failed to enable 2FA for {phone}: {str(e)}")
            raise HTTPException(status_code=400, detail=f"Failed to enable 2FA: {str(e)}")
        
