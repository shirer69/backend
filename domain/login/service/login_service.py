from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError, PhoneCodeInvalidError
import os
import logging
from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv


load_dotenv()
# -----------------------
# Basic Config
# -----------------------

api_id = os.getenv("API_ID")
api_hash = os.getenv("API_HASH")


# session_base_path = "sessions"
session_base_path = "/tmp/sessions"


os.makedirs(session_base_path, exist_ok=True)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PHONE_HASH_STORE = {}


class LoginService:
    @staticmethod
    async def get_client(phone: str) -> TelegramClient:
        print(f"api_id {api_id}")
        print(f"api_hash {api_hash}")

        session_name = os.path.join(session_base_path, f"session_{phone.replace('+', '')}")
        return TelegramClient(session_name, api_id, api_hash, connection_retries=3)
    

    @staticmethod
    async def initiate_login(phone: str):
        """Send Telegram code to the given phone"""
        session_name = os.path.join(session_base_path, f"session_{phone.replace('+', '')}")
        session_file = f"{session_name}.session"

        # 🔹 Step 2: Delete old session file (only when starting a new login)
        if os.path.exists(session_file):
            try:
                os.remove(session_file)
                logger.info(f"Old session file deleted before new login: {session_file}")
            except Exception as e:
                logger.error(f"Failed to delete existing session file {session_file}: {str(e)}")

        # 🔹 Step 3: Create Telegram client
        client = await LoginService.get_client(phone)
        await client.connect()

        try:
            if await client.is_user_authorized():
                user = await client.get_me()
                await client.disconnect()
                return {
                    "message": "Already logged in",
                    "user": user.first_name,
                    "phone": phone,
                }

            result = await client.send_code_request(phone)
            PHONE_HASH_STORE[phone] = result.phone_code_hash  # Save for later verification
            await client.disconnect()

            logger.info(f"Code sent to {phone}")
            return {
                "message": "Code sent successfully",
                "phone": phone,
                "phone_code_hash": result.phone_code_hash,  # optional, can remove in prod
            }

        except Exception as e:
            logger.error(f"Error sending code to {phone}: {str(e)}")
            await client.disconnect()
            raise HTTPException(status_code=400, detail=f"Failed to send code: {str(e)}")


    @staticmethod
    async def verify_code(phone: str, code: str,phone_hash:str):
        """Verify Telegram login code"""
        client = await LoginService.get_client(phone)
        await client.connect()
        try:
            phone_code_hash = phone_hash
            if not phone_code_hash:
                raise HTTPException(status_code=400, detail="Missing phone_code_hash. Start login again.")

            await client.sign_in(phone=phone, code=code, phone_code_hash=phone_code_hash)
            user = await client.get_me()
            await client.disconnect()

            return {"message": "Login successful", "user": user.first_name, "phone": phone}

        except PhoneCodeInvalidError:
            await client.disconnect()
            raise HTTPException(status_code=400, detail="Invalid verification code")
        except SessionPasswordNeededError:
            await client.disconnect()
            raise HTTPException(status_code=401, detail="2FA password required")
        except Exception as e:
            await client.disconnect()
            logger.error(f"Error verifying code for {phone}: {str(e)}")
            raise HTTPException(status_code=400, detail=f"Code verification failed: {str(e)}")



    @staticmethod
    async def verify_2fa_password(phone: str, password: str):
        """Verify Telegram 2FA password"""
        client = await LoginService.get_client(phone)
        await client.connect()
        try:
            await client.sign_in(password=password)
            user = await client.get_me()
            await client.disconnect()
            return {"message": "Login successful (2FA)", "user": user.first_name, "phone": phone}
        except Exception as e:
            await client.disconnect()
            logger.error(f"2FA failed for {phone}: {str(e)}")
            raise HTTPException(status_code=400, detail=f"2FA failed: {str(e)}")




    # @staticmethod
    # async def get_profile(phone: str):
    #     client = await LoginService.get_client(phone)
    #     await client.connect()

    #     try:
    #         if not await client.is_user_authorized():
    #             await client.disconnect()
    #             raise HTTPException(status_code=401, detail="User not logged in. Please log in first.")

    #         me = await client.get_me()
    #         await client.disconnect()

    #         profile_data = {
    #             "id": me.id,
    #             "first_name": me.first_name,
    #             "last_name": me.last_name,
    #             "username": me.username,
    #             "phone": me.phone,
    #             "bio": me.bot_info_description if me.bot else getattr(me, 'about', None),
    #             "is_bot": me.bot,
    #         }

    #         return {"message": "Profile fetched successfully", "profile": profile_data}

    #     except Exception as e:
    #         await client.disconnect()
    #         logger.error(f"Failed to fetch profile for {phone}: {str(e)}")
    #         raise HTTPException(status_code=400, detail=f"Failed to fetch profile: {str(e)}")


    @staticmethod
    async def get_profile(phone: str):
        client = await LoginService.get_client(phone)
        await client.connect()

        try:
            if not await client.is_user_authorized():
                await client.disconnect()
                raise HTTPException(status_code=401, detail="User not logged in. Please log in first.")

            me = await client.get_me()
            await client.disconnect()

            session_filename = f"session_{phone.replace('+', '')}.session"
            session_path = os.path.join(session_base_path, session_filename)
            # session_download_url = f"/sessions/{session_filename}"

            profile_data = {
                "id": me.id,
                "first_name": me.first_name,
                "last_name": me.last_name,
                "username": me.username,
                "phone": me.phone,
                "bio": me.bot_info_description if me.bot else getattr(me, 'about', None),
                "is_bot": me.bot,
                # "session_download_url": session_download_url,
                "session_download_url": None,

            }

            return {
                "message": "Profile fetched successfully",
                "profile": profile_data,
            }

        except Exception as e:
            await client.disconnect()
            logger.error(f"Failed to fetch profile for {phone}: {str(e)}")
            raise HTTPException(status_code=400, detail=f"Failed to fetch profile: {str(e)}")
