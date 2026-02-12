
from typing import Any
from fastapi import APIRouter, Depends, Body
from fastapi.security import OAuth2PasswordRequestForm
from app.services.auth_service import AuthService
from app.api import deps
from app.schemas.user import UserCreate, UserResponse, OTPVerify, ForgotPassword, ResetPassword
from app.schemas.token import Token

router = APIRouter()

@router.post("/register", response_model=UserResponse)
async def register(
    user_in: UserCreate,
    auth_service: AuthService = Depends(deps.get_auth_service)
) -> Any:
    return await auth_service.register(user_in)

@router.post("/verify-registration")
async def verify_registration(
    otp_in: OTPVerify,
    auth_service: AuthService = Depends(deps.get_auth_service)
) -> Any:
    await auth_service.verify_registration(otp_in.email, otp_in.otp)
    return {"message": "Registration verified successfully"}

@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_service: AuthService = Depends(deps.get_auth_service)
) -> Any:
    # Adapt OAuth2PasswordRequestForm to UserLogin schema logic (email/username + password)
    # Here username in form_data is email
    from app.schemas.user import UserLogin
    user_in = UserLogin(email=form_data.username, password=form_data.password)
    return await auth_service.login(user_in)

@router.post("/forgot-password")
async def forgot_password(
    forgot_in: ForgotPassword,
    auth_service: AuthService = Depends(deps.get_auth_service)
) -> Any:
    await auth_service.forgot_password(forgot_in.email)
    return {"message": "If the email exists, an OTP has been sent"}

@router.post("/verify-reset-otp")
async def verify_reset_otp(
    otp_in: OTPVerify,
    auth_service: AuthService = Depends(deps.get_auth_service)
) -> Any:
    await auth_service.verify_reset_password_otp(otp_in.email, otp_in.otp)
    return {"message": "OTP is valid"}

@router.post("/reset-password")
async def reset_password(
    reset_in: ResetPassword,
    auth_service: AuthService = Depends(deps.get_auth_service)
) -> Any:
    await auth_service.reset_password(reset_in.email, reset_in.otp, reset_in.new_password)
    return {"message": "Password reset successfully"}

@router.get("/google/login")
async def google_login():
    from app.core.config import settings
    from fastapi.responses import RedirectResponse
    
    return RedirectResponse(
        f"https://accounts.google.com/o/oauth2/auth?response_type=code&client_id={settings.GOOGLE_CLIENT_ID}&redirect_uri={settings.GOOGLE_REDIRECT_URI}&scope=openid%20email%20profile&access_type=offline"
    )

@router.get("/google/callback", response_model=Token)
async def google_callback(
    code: str,
    auth_service: AuthService = Depends(deps.get_auth_service)
) -> Any:
    return await auth_service.google_login(code)
