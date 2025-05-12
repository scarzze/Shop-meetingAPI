# Authentication Service

This service handles user authentication and authorization for the Shop-meetingAPI microservices architecture.

## Features

- User registration and login
- JWT-based authentication
- Token verification and refresh
- Rate limiting for login attempts
- Shared authentication middleware for other services
- CORS support for cross-service communication

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables (create .env file):
```
DATABASE_URL=postgresql://hosea:moringa001@localhost:5432/hosea
JWT_SECRET_KEY=your_super_secret_jwt_key
```

3. Initialize the database:
```bash
flask db upgrade
```

4. Run the service:
```bash
python run.py
```

## API Endpoints

### POST /auth/register
Register a new user.
```json
{
    "email": "user@example.com",
    "password": "password123",
    "first_name": "John",
    "last_name": "Doe"
}
```

### POST /auth/login
Login and receive JWT tokens.
```json
{
    "email": "user@example.com",
    "password": "password123"
}
```

### GET /auth/verify
Verify a JWT token (requires Authorization header).

### POST /auth/refresh
Get a new access token using a refresh token.

## Middleware Usage

Other services can use the authentication middleware by importing from auth-service:

```python
from app.utils.decorators import login_required, verify_auth_service

@app.route('/protected')
@login_required
def protected_route():
    return {"message": "This is a protected route"}
```