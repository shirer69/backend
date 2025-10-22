from pydantic import BaseModel

class LoginRequest(BaseModel):
    phone: str  # Phone number with country code, e.g., +1234567890

class CodeRequest(BaseModel):
    phone: str
    code: str
    phone_hash: str

class PasswordRequest(BaseModel):
    phone: str
    password: str


class Enable2FARequest(BaseModel):
    phone: str
    new_password: str
    hint: str = ""