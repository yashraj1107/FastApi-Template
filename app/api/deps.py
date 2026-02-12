
from typing import AsyncGenerator
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession
from app.core import security
from app.core.config import settings
from app.db.session import get_db
from app.models.user import User
from app.repos.user_repo import UserRepo
from app.repos.otp_repo import OTPRepo
from app.services.email_service import EmailService
from app.services.auth_service import AuthService
from app.schemas.token import TokenPayload

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")

async def get_user_repo(db: AsyncSession = Depends(get_db)) -> UserRepo:
    return UserRepo(db)

async def get_otp_repo(db: AsyncSession = Depends(get_db)) -> OTPRepo:
    return OTPRepo(db)

async def get_email_service() -> EmailService:
    return EmailService()

async def get_auth_service(
    user_repo: UserRepo = Depends(get_user_repo),
    otp_repo: OTPRepo = Depends(get_otp_repo),
    email_service: EmailService = Depends(get_email_service)
) -> AuthService:
    return AuthService(user_repo, otp_repo, email_service)

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    user_repo: UserRepo = Depends(get_user_repo)
) -> User:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        token_data = TokenPayload(**payload)
    except (JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    user = await user_repo.get_user_by_email(token_data.sub)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return user
