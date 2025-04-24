# E-commerce Microservices Project

## Initial Environment Setup (All Developers)

1. Clone the repository and set up Python virtual environment:
```bash
git clone <repository-url>
cd Shop-meetingAPI
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
```

2. Install common dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables (create .env in your service directory):
```env
AUTH_SERVICE_URL=http://localhost:5001
DATABASE_URL=sqlite:///your_service.db
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret
```

## Service-Specific Setup and Guidelines

### 🧑‍💻 Dev 1: Authentication Service (Port 5001)
- Status: Implemented ✅
- Primary Files: `/services/auth/*`
- Running the service:
```bash
cd services/auth
python src/app.py
```

### 🧑‍💻 Dev 2: Product Service (Port 5002)
- Directory: `/services/product/*`
- Key Authentication Requirements:
  ```python
  # In src/app.py
  from shared.auth_middleware import require_auth
  
  # Public routes (no auth needed):
  @app.route('/products', methods=['GET'])
  def list_products():
      pass
      
  # Protected routes (auth required):
  @app.route('/products', methods=['POST'])
  @require_auth
  def create_product():
      current_user = request.user
      # Only admin can create products
      pass
  ```
- Required Models:
  - Product (name, description, price, stock)
  - Category (name, description)
  - Review (rating, comment, user_id)

### 🧑‍💻 Dev 3: Cart Service (Port 5003)
- Directory: `/services/cart/*`
- Key Authentication Requirements:
  ```python
  # All cart operations require authentication
  @app.route('/cart', methods=['GET'])
  @require_auth
  def get_cart():
      user_id = request.user['id']
      # Return user's cart items
      pass
  
  @app.route('/cart/items', methods=['POST'])
  @require_auth
  def add_to_cart():
      user_id = request.user['id']
      # Add item to user's cart
      pass
  ```
- Required Models:
  - Cart (user_id, created_at)
  - CartItem (cart_id, product_id, quantity)

### 🧑‍💻 Dev 4: Order Service (Port 5004)
- Directory: `/services/order/*`
- Key Authentication Requirements:
  ```python
  # All order operations require authentication
  @app.route('/orders', methods=['POST'])
  @require_auth
  def create_order():
      user_id = request.user['id']
      # Create order from user's cart
      pass
  
  @app.route('/orders/<order_id>', methods=['GET'])
  @require_auth
  def get_order(order_id):
      user_id = request.user['id']
      # Ensure order belongs to user
      pass
  ```
- Required Models:
  - Order (user_id, status, total_amount)
  - OrderItem (order_id, product_id, quantity, price)

### 🧑‍💻 Dev 5: Profile Service (Port 5005)
- Directory: `/services/profile/*`
- Key Authentication Requirements:
  ```python
  # All profile operations require authentication
  @app.route('/profile', methods=['GET'])
  @require_auth
  def get_profile():
      user_id = request.user['id']
      # Return user's profile
      pass
  
  @app.route('/profile/wishlist', methods=['GET'])
  @require_auth
  def get_wishlist():
      user_id = request.user['id']
      # Return user's wishlist
      pass
  ```
- Required Models:
  - Profile (user_id, full_name, address, phone)
  - Wishlist (user_id, product_id)

### 🧑‍💻 Dev 6: Support Service (Port 5006)
- Directory: `/services/support/*`
- Key Authentication Requirements:
  ```python
  # Mix of public and protected routes
  @app.route('/faqs', methods=['GET'])
  def list_faqs():
      # Public access to FAQs
      pass
  
  @app.route('/tickets', methods=['POST'])
  @require_auth
  def create_ticket():
      user_id = request.user['id']
      user_email = request.user['email']
      # Create support ticket
      pass
  ```
- Required Models:
  - Ticket (user_id, subject, description, status)
  - FAQ (question, answer, category)

## Testing Your Service

1. Start the Auth Service first:
```bash
cd services/auth
python src/app.py
```

2. Get a test token:
```bash
# Register a test user
curl -X POST http://localhost:5001/auth/register \
     -H "Content-Type: application/json" \
     -d '{"email": "test@example.com", "password": "password123"}'

# Login to get token
curl -X POST http://localhost:5001/auth/login \
     -H "Content-Type: application/json" \
     -d '{"email": "test@example.com", "password": "password123"}'
```

3. Test your protected endpoints:
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
     http://localhost:YOUR_PORT/your-endpoint
```

## Error Handling Guidelines

1. Authentication Errors:
```python
@app.errorhandler(401)
def unauthorized_error(error):
    return jsonify({'error': 'Unauthorized access'}), 401

@app.errorhandler(403)
def forbidden_error(error):
    return jsonify({'error': 'Forbidden'}), 403

@app.errorhandler(503)
def service_unavailable_error(error):
    return jsonify({'error': 'Service temporarily unavailable'}), 503
```

2. Data Validation Errors:
```python
def validate_request_data(data, required_fields):
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        return jsonify({
            'error': 'Missing required fields',
            'fields': missing_fields
        }), 400
```

## Service Communication

1. Inter-service communication (example):
```python
import requests

def get_product_details(product_id, auth_token):
    try:
        response = requests.get(
            f'http://localhost:5002/products/{product_id}',
            headers={'Authorization': f'Bearer {auth_token}'}
        )
        return response.json() if response.ok else None
    except requests.RequestException:
        return None
```

## Database Migrations

Each service should handle its own database migrations:
```bash
cd your_service_directory
flask db init    # First time only
flask db migrate -m "Initial migration"
flask db upgrade
```

## Monitoring and Logging

Add to your service's app.py:
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(service)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
```

## Running in Development

1. Start each service in a separate terminal:
```bash
# Terminal 1 - Auth Service
cd services/auth && python src/app.py

# Terminal 2 - Your Service
cd services/your_service && python src/app.py
```

2. Monitor logs in each terminal for debugging

## Production Considerations

1. Use environment variables for all configurations
2. Implement proper logging
3. Add health check endpoints
4. Use proper CORS settings
5. Implement rate limiting
6. Add API documentation

## Overview
This is a microservices-based e-commerce system with the following services:
- Auth Service (Port 5001): Handles user authentication
- Product Service (Port 5002): Manages product catalog
- Cart Service (Port 5003): Manages shopping cart
- Order Service (Port 5004): Handles order processing
- Profile Service (Port 5005): Manages user profiles
- Support Service (Port 5006): Handles customer support

## Authentication Integration Guide

### 1. Setup Authentication in Your Service

Each service needs to configure authentication by:

1. Import the shared auth middleware in your routes:
```python
from shared.auth_middleware import require_auth
```

2. Add AUTH_SERVICE_URL to your service's config/config.py:
```python
class Config:
    AUTH_SERVICE_URL = os.environ.get('AUTH_SERVICE_URL', 'http://localhost:5001')
    # ... other config settings
```

### 2. Protecting Routes

To protect any endpoint, use the @require_auth decorator:

```python
@app.route('/your-endpoint', methods=['POST'])
@require_auth
def protected_endpoint():
    # Access authenticated user information
    current_user = request.user
    user_id = current_user['id']
    user_email = current_user['email']
    
    # Your endpoint logic here
    return jsonify({'message': 'Success'})
```

### 3. Working with User Authentication

The @require_auth decorator provides:
- Automatic token validation
- User information in request.user
- Proper error responses for invalid/missing tokens

Example user information available in request.user:
```python
{
    'id': 1,
    'email': 'user@example.com',
    'created_at': '2025-04-24T18:49:32'
}
```

### 4. Error Handling

Authentication errors you should handle:
- 401: Invalid or missing token
- 403: Insufficient permissions
- 503: Auth service unavailable

Example error handling:
```python
@app.errorhandler(401)
def unauthorized_error(error):
    return jsonify({'error': 'Unauthorized access'}), 401

@app.errorhandler(503)
def service_unavailable_error(error):
    return jsonify({'error': 'Authentication service unavailable'}), 503
```

## Testing Your Protected Routes

1. Get an authentication token:
```bash
curl -X POST -H "Content-Type: application/json" \
     -d '{"email": "user@gmail.com", "password": "secure123"}' \
     http://localhost:5001/auth/login
```

2. Use the token in your requests:
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
     http://localhost:YOUR_PORT/your-endpoint
```

## Service Dependencies
- All services depend on the Auth Service for token verification
- Cart Service depends on Product Service for product validation
- Order Service depends on Cart Service for checkout
- Profile Service provides user preferences to other services

## Best Practices

1. Always use @require_auth for endpoints that:
   - Modify data (POST, PUT, DELETE)
   - Access user-specific information
   - Require user context

2. Public endpoints (no auth needed):
   - Product listing
   - Public information
   - Health checks

3. User Context:
   - Always use request.user['id'] to associate data with users
   - Validate user permissions before sensitive operations
   - Don't trust client-provided user IDs

4. Error Handling:
   - Always handle authentication errors gracefully
   - Provide clear error messages
   - Log authentication failures appropriately

5. Testing:
   - Include authentication in your test cases
   - Mock auth service in unit tests
   - Test both successful and failed auth scenarios