from fastapi import FastAPI
from domain.login.schema.login_schema import LoginRequest,CodeRequest,PasswordRequest,Enable2FARequest
from domain.login.service.login_service import LoginService
# from domain.two_fa.service.two_fa_service import Enable_2fa_password
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

app = FastAPI()


origins = [
    "http://localhost:3000", 
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,      
    allow_credentials=True,
    allow_methods=["*"],            
    allow_headers=["*"],           
)
# app.mount("/sessions", StaticFiles(directory="sessions"), name="sessions")
@app.get("/")
async def root():
    return {"message": "Hello, FastAPI new!"}

@app.post("/login")
async def login(request: LoginRequest):
    return await LoginService.initiate_login(request.phone)

@app.post("/verify-code")
async def verify_code(request: CodeRequest):
    return await LoginService.verify_code(request.phone, request.code,request.phone_hash)

@app.post("/verify-2fa")
async def verify_2fa(request: PasswordRequest):
    return await LoginService.verify_2fa_password(request.phone, request.password)

# @app.post("/enable_2fa")
# async def enable_2fa(data: Enable2FARequest):
#     return await Enable_2fa_password.enable_2fa_password(
#         phone=data.phone,
#         new_password=data.new_password,
#         hint=data.hint
#     )


@app.get("/get_profile")
async def get_profile(phone: str):
    return await LoginService.get_profile(phone)