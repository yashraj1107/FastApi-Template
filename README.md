# Enterprise FastAPI Template

A production-ready, modular, and scalable **FastAPI** template designed for enterprise applications. Built with performance and developer experience in mind, using **Async SQLAlchemy**, **PostgreSQL**, and **uv** for dependency management.

## 🚀 Features

-   **Modular Architecture**: Domain-driven design structure (`api`, `core`, `services`, `repos`, `models`).
-   **High Performance**: Fully async stack with `asyncpg` and `SQLAlchemy 2.0`.
-   **Robust Authentication**:
    -   JWT (JSON Web Tokens) access authentication.
    -   **Google OAuth 2.0** integration.
    -   Email/Password registration with OTP verification.
    -   Secure Password Reset flow (OTP-based).
-   **Database**: PostgreSQL integration with **Alembic** migrations.
-   **Dependency Management**: Modern and fast dependency management using `uv`.
-   **Testing**: Pre-configured `pytest` suite with async support (`pytest-asyncio`, `httpx`).

## 🛠️ Tech Stack

-   **Framework**: FastAPI
-   **Database**: PostgreSQL
-   **ORM**: SQLAlchemy (Async)
-   **Migrations**: Alembic
-   **Package Manager**: uv
-   **Server**: Uvicorn

## 📂 Project Structure

```bash
/
├── app/
│   ├── api/          # API Routers and Dependencies
│   ├── core/         # Config, Security, Logging
│   ├── db/           # Database Session and Base
│   ├── models/       # SQLAlchemy Models
│   ├── repos/        # Repository Pattern Classes
│   ├── schemas/      # Pydantic Schemas
│   ├── services/     # Business Logic
│   └── main.py       # Application Entrypoint
├── alembic/          # Database Migrations
├── tests/            # Test Suite
├── scripts/          # Utility Scripts
└── pyproject.toml    # Project Dependencies
```

## ⚡ Getting Started

### Prerequisites

-   **Python 3.11+**
-   **PostgreSQL** (running locally or via Docker)
-   **uv** (Install via `pip install uv` or `curl -LsSf https://astral.sh/uv/install.sh | sh`)

### Installation

1.  **Clone the repository**
    ```bash
    git clone https://github.com/your-username/fastapi-template.git
    cd fastapi-template
    ```

2.  **Install dependencies**
    ```bash
    uv sync
    ```

3.  **Environment Setup**
    Create a `.env` file in the root directory (copy from example if available, or use the following template):
    ```env
    PROJECT_NAME="FastAPI Enterprise Template"
    API_V1_STR="/api/v1"
    SECRET_KEY="your_super_secret_key"
    ACCESS_TOKEN_EXPIRE_MINUTES=30
    
    # Database
    POSTGRES_SERVER=localhost
    POSTGRES_USER=postgres
    POSTGRES_PASSWORD=postgres
    POSTGRES_DB=app_db
    
    # Google OAuth (Optional)
    GOOGLE_CLIENT_ID=your_google_client_id
    GOOGLE_CLIENT_SECRET=your_google_client_secret
    GOOGLE_REDIRECT_URI=http://localhost:8000/api/v1/auth/google/callback
    
    # Email (Mock)
    SMTP_TLS=True
    SMTP_PORT=587
    SMTP_HOST=smtp.gmail.com
    SMTP_USER=user@example.com
    SMTP_PASSWORD=password
    ```

4.  **Database Setup**
    Ensure your Postgres server is running. Then run migrations:
    ```bash
    # Create DB (if it doesn't exist)
    uv run python scripts/create_db.py
    
    # Run Migrations
    uv run alembic upgrade head
    ```

### 🏃‍♂️ Running the Server

Start the development server with hot-reloading:

```bash
uv run uvicorn app.main:app --reload
```

The API will be available at:
-   **Docs**: http://127.0.0.1:8000/docs
-   **ReDoc**: http://127.0.0.1:8000/redoc

## 🧪 Running Tests

Run the test suite using `pytest`:

```bash
uv run pytest
```

## 🔒 Authentication Flows

### Register (Email/Password)
1.  **POST** `/api/v1/auth/register` with email and password.
2.  Receive OTP (mocked in console logs).
3.  **POST** `/api/v1/auth/verify-registration` with email and OTP.
4.  User is now active and verified.

### Login (Google OAuth)
1.  **GET** `/api/v1/auth/google/login`.
2.  Redirect to Google -> Sign In.
3.  Redirect back to callback -> Receive JWT Access Token.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.