
from datetime import datetime
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.otp import OTP

class OTPRepo:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_otp(self, email: str, code: str, type: str, expires_at: datetime) -> OTP:
        db_otp = OTP(email=email, code=code, type=type, expires_at=expires_at)
        self.db.add(db_otp)
        await self.db.commit()
        await self.db.refresh(db_otp)
        return db_otp

    async def get_latest_valid_otp(self, email: str, type: str) -> Optional[OTP]:
        # Get the latest unused OTP that hasn't expired
        result = await self.db.execute(
            select(OTP)
            .where(
                OTP.email == email,
                OTP.type == type,
                OTP.is_used == False,
                OTP.expires_at > datetime.utcnow()
            )
            .order_by(OTP.created_at.desc())
        )
        return result.scalars().first()

    async def mark_as_used(self, otp: OTP) -> OTP:
        otp.is_used = True
        self.db.add(otp)
        await self.db.commit()
        await self.db.refresh(otp)
        return otp
