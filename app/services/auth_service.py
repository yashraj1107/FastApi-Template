
from datetime import timedelta
from fastapi import HTTPException, status
from app.models.user import User
from app.repos.user_repo import UserRepo
from app.repos.otp_repo import OTPRepo
from app.schemas.user import UserCreate, UserLogin, UserResponse
from app.schemas.token import Token
from app.core.security import get_password_hash, verify_password, create_access_token
from app.utils.otp import generate_otp, get_otp_expiry
from app.services.email_service import EmailService

class AuthService:
    def __init__(self, user_repo: UserRepo, otp_repo: OTPRepo, email_service: EmailService):
        self.user_repo = user_repo
        self.otp_repo = otp_repo
        self.email_service = email_service

    async def register(self, user_in: UserCreate) -> UserResponse:
        existing_user = await self.user_repo.get_user_by_email(user_in.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        hashed_password = get_password_hash(user_in.password)
        
        user = await self.user_repo.create_user(user_in, hashed_password)
        
        # Generate and send OTP
        otp_code = generate_otp()
        expiry = get_otp_expiry()
        await self.otp_repo.create_otp(user.email, otp_code, "register", expiry)
        await self.email_service.send_otp_email(user.email, otp_code, "Registration")
        
        return user

    async def verify_registration(self, email: str, otp: str) -> bool:
        user = await self.user_repo.get_user_by_email(email)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        valid_otp = await self.otp_repo.get_latest_valid_otp(email, "register")
        if not valid_otp or valid_otp.code != otp:
             raise HTTPException(status_code=400, detail="Invalid or expired OTP")
        
        # Mark OTP as used
        await self.otp_repo.mark_as_used(valid_otp)
        
        # Verify user
        user.is_verified = True
        user.is_active = True # Ensure active
        await self.user_repo.update_user(user)
        return True

    async def login(self, user_in: UserLogin) -> Token:
        user = await self.user_repo.get_user_by_email(user_in.email)
        if not user or not verify_password(user_in.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        if not user.is_active:
             raise HTTPException(status_code=400, detail="Inactive user")
        
        if not user.is_verified:
            raise HTTPException(status_code=400, detail="User not verified. Please verify your email.")

        access_token_expires = timedelta(minutes=30)
        access_token = create_access_token(
            subject=user.email, expires_delta=access_token_expires
        )
        return Token(access_token=access_token, token_type="bearer")

    async def forgot_password(self, email: str):
        user = await self.user_repo.get_user_by_email(email)
        if not user:
             return 

        otp_code = generate_otp()
        expiry = get_otp_expiry()
        await self.otp_repo.create_otp(email, otp_code, "reset_password", expiry)
        await self.email_service.send_otp_email(email, otp_code, "Password Reset")

    async def verify_reset_password_otp(self, email: str, otp: str) -> bool:
         # Just verifies the OTP is valid, does not reset yet. 
         # Used if the UI wants to show a "valid OTP" state before asking for new password
         valid_otp = await self.otp_repo.get_latest_valid_otp(email, "reset_password")
         if not valid_otp or valid_otp.code != otp:
             raise HTTPException(status_code=400, detail="Invalid or expired OTP")
         return True

    async def reset_password(self, email: str, otp: str, new_password: str):
        valid_otp = await self.otp_repo.get_latest_valid_otp(email, "reset_password")
        if not valid_otp or valid_otp.code != otp:
             raise HTTPException(status_code=400, detail="Invalid or expired OTP")
        
        user = await self.user_repo.get_user_by_email(email)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
            
        hashed_password = get_password_hash(new_password)
        user.hashed_password = hashed_password
        await self.user_repo.update_user(user)
        
        await self.otp_repo.mark_as_used(valid_otp)
