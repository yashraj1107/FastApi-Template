
import pytest
from typing import AsyncGenerator
from httpx import AsyncClient
from app.main import app
from app.db.session import AsyncSessionLocal

@pytest.fixture
async def db() -> AsyncGenerator:
    async with AsyncSessionLocal() as session:
        yield session

@pytest.fixture
async def client() -> AsyncGenerator:
    from httpx import ASGITransport
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c
