# Profile Service

A streamlined user profile management service for e-commerce platforms focusing on core functionality and maintainability.

## Features

### Profile Management
- User profile data with comprehensive validation
- Multiple address management
- User preferences
- Wishlist management

### Security
- JWT authentication
- Input validation using Marshmallow schemas
- Security headers and CORS policy

### Notifications
- Integrated notification system
- Price drop alerts for wishlist items
- Personalized product recommendations
- Configurable notification preferences

## Technical Stack

- **Framework**: Flask 2.2.3
- **Database**: PostgreSQL with SQLAlchemy
- **Authentication**: JWT (Flask-JWT-Extended)
- **Validation**: Marshmallow
- **Security**: Cryptography

## Setup

1. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables (copy from .env.example):
```bash
cp .env.example .env
# Edit .env with your configurations
```

4. Initialize database:
```bash
flask db upgrade
```

5. Start the API server:
```bash
gunicorn --bind 0.0.0.0:5000 run:app
```

## Docker Setup

1. Build and start services:
```bash
docker-compose up --build
```

## Core APIs

### Profile Operations
```
GET    /profile/<user_id>     # Get user profile
PATCH  /profile              # Update profile
```

### Address Management
```
GET    /addresses            # List addresses
POST   /addresses           # Add address
PUT    /addresses/<id>      # Update address
DELETE /addresses/<id>      # Delete address
```

### Wishlist
```
GET    /wishlist           # Get wishlist items
POST   /wishlist/<id>      # Add to wishlist
DELETE /wishlist/<id>      # Remove from wishlist
```

## Data Models

### Profile
- Basic user information
- Contact details
- Preferences
- Notification settings

### Address
- Multiple addresses per user
- Shipping/billing types
- Default address support

### Wishlist
- Product tracking
- Price alert preferences

## Security

1. Authentication:
   - JWT-based authentication
   - Input validation with Marshmallow schemas

2. Data Protection:
   - Security headers
   - CORS policy

## Development

1. Running tests:
```bash
python -m pytest
```

2. Database migrations:
```bash
flask db migrate -m "migration message"
flask db upgrade
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

## License

MIT