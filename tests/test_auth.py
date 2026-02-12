
import pytest
from httpx import AsyncClient
from app.models.otp import OTP
from app.utils.otp import generate_otp
from sqlalchemy.future import select
from app.db.session import AsyncSessionLocal

# Helper to get OTP from DB for testing
async def get_otp(email: str, type: str):
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(OTP).where(OTP.email == email, OTP.type == type).order_by(OTP.created_at.desc())
        )
        return result.scalars().first()

@pytest.mark.asyncio
async def test_register_flow(client: AsyncClient):
    import uuid
    email = f"test_{uuid.uuid4()}@example.com"
    password = "password123"
    
    # 1. Register
    response = await client.post("/api/v1/auth/register", json={"email": email, "password": password})
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == email
    assert data["is_active"] == True # Default is active
    assert data["is_verified"] == False

    # 2. Get OTP (simulate email)
    otp_record = await get_otp(email, "register")
    assert otp_record is not None
    otp_code = otp_record.code

    # 3. Verify Registration
    response = await client.post("/api/v1/auth/verify-registration", json={"email": email, "otp": otp_code})
    assert response.status_code == 200
    assert response.json()["message"] == "Registration verified successfully"

    # 4. Login
    response = await client.post("/api/v1/auth/login", data={"username": email, "password": password})
    assert response.status_code == 200
    token_data = response.json()
    assert "access_token" in token_data
    assert token_data["token_type"] == "bearer"

@pytest.mark.asyncio
async def test_reset_password_flow(client: AsyncClient):
    import uuid
    email = f"reset_{uuid.uuid4()}@example.com"
    password = "password123"
    new_password = "newpassword456"

    # Create user first
    await client.post("/api/v1/auth/register", json={"email": email, "password": password})
    # Verify manually to allow login (though forgot password doesn't need login, reset does need user)
    otp_record = await get_otp(email, "register")
    await client.post("/api/v1/auth/verify-registration", json={"email": email, "otp": otp_record.code})

    # 1. Forgot Password
    response = await client.post("/api/v1/auth/forgot-password", json={"email": email})
    assert response.status_code == 200

    # 2. Get OTP
    otp_record = await get_otp(email, "reset_password")
    assert otp_record is not None
    otp_code = otp_record.code

    # 3. Verify OTP
    response = await client.post("/api/v1/auth/verify-reset-otp", json={"email": email, "otp": otp_code})
    assert response.status_code == 200

    # 4. Reset Password
    response = await client.post("/api/v1/auth/reset-password", json={"email": email, "otp": otp_code, "new_password": new_password})
    assert response.status_code == 200

    # 5. Login with new password
    response = await client.post("/api/v1/auth/login", data={"username": email, "password": new_password})
    assert response.status_code == 200
