
import asyncio
import uuid
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.db.session import AsyncSessionLocal
from app.models.otp import OTP
from sqlalchemy.future import select

async def verify_auth_flow():
    print("Starting Main Auth Verification...")
    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            email = f"verify_{uuid.uuid4()}@example.com"
            password = "password123"
            
            print(f"1. Registering user: {email}")
            response = await client.post("/api/v1/auth/register", json={"email": email, "password": password})
            print(f"Register Status: {response.status_code}")
            print(f"Register Response: {response.text}")
            
            if response.status_code != 200:
                print("!!! Registration Failed !!!")
                return

            print("2. Getting OTP from DB...")
            async with AsyncSessionLocal() as session:
                result = await session.execute(
                    select(OTP).where(OTP.email == email, OTP.type == "register").order_by(OTP.created_at.desc())
                )
                otp_record = result.scalars().first()
            
            if not otp_record:
                print("!!! OTP not found in DB !!!")
                return
            
            otp_code = otp_record.code
            print(f"Found OTP: {otp_code}")

            print("3. Verifying Registration...")
            response = await client.post("/api/v1/auth/verify-registration", json={"email": email, "otp": otp_code})
            print(f"Verify Status: {response.status_code}")
            print(f"Verify Response: {response.text}")

            if response.status_code != 200:
                print("!!! Verification Failed !!!")
                return

            print("4. Logging in...")
            response = await client.post("/api/v1/auth/login", data={"username": email, "password": password})
            print(f"Login Status: {response.status_code}")
            print(f"Login Response: {response.text}")

            if response.status_code == 200:
                print(">>> SUCCESS: Auth Flow Verified! <<<")
            else:
                print("!!! Login Failed !!!")
    except Exception as e:
        print(f"!!! EXCEPTION: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(verify_auth_flow())
