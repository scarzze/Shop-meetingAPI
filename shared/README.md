# Shop Meeting API Authentication System

This shared authentication system allows Shop Meeting API microservices to work properly with or without DEBUG_MODE.

## Overview

The shared authentication utility provides:

1. A robust token verification mechanism with multiple fallback options
2. Consistent middleware/decorators across all services
3. Backward compatibility with existing code
4. Production-ready features for secure inter-service communication

## How It Works

When DEBUG_MODE is disabled (production mode), the authentication system:

1. First attempts to verify tokens with the Auth Service
2. Falls back to local token verification using the JWT secret if the Auth Service is unavailable
3. Properly handles service-to-service authentication

## Integration with Services

The `setup.py` script will install the authentication utility to all services. After installation:

1. Each service will have access to the same authentication decorators
2. The decorators can be used consistently across services
3. Services will work without DEBUG_MODE

## Usage

### Installation

Run the setup script to install the shared authentication to all services:

```bash
python3 shared/setup.py
```

### In Your Flask Routes

Replace existing authentication decorators with the shared ones:

```python
from utils.auth_utils import auth_required, admin_required, support_agent_required

@app.route('/your-protected-endpoint')
@auth_required
def protected_endpoint():
    # Access the authenticated user with request.user
    user_id = request.user['id']
    return jsonify({"message": "Protected data"})
```

### Environment Configuration

In production, disable DEBUG_MODE by setting:

```
DEBUG_MODE=false
```

Make sure all services have the same JWT_SECRET_KEY to enable local token verification as a fallback mechanism.

## Benefits

- **Reliability**: Services continue to work even if the Auth Service is temporarily unavailable
- **Security**: Proper token verification in all environments
- **Consistency**: Same authentication logic across all services
- **Flexibility**: Easy to switch between development and production modes
