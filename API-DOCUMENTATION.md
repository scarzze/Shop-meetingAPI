# Shop Meeting API Documentation

## API Gateway

The API Gateway serves as the central entry point to all microservices in the Shop Meeting application. It routes requests to the appropriate service and handles cross-cutting concerns like CORS.

**Base URL**: `http://localhost`

## Health Check

**Endpoint**: `/health`
**Method**: GET
**Description**: Verifies if the API Gateway is operating correctly
**Response**: 
```json
{
  "status": "healthy",
  "timestamp": "2025-05-12T02:21:17+03:00"
}
```

## Authentication Service

API routes for user authentication and authorization.

### Login

**Endpoint**: `/api/auth/login`
**Method**: POST
**Description**: Authenticates a user and returns a JWT token
**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "secure_password"
}
```
**Response**:
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user_id": 1
}
```

### Register

**Endpoint**: `/api/auth/register`
**Method**: POST
**Description**: Creates a new user account
**Request Body**:
```json
{
  "email": "newuser@example.com",
  "password": "secure_password",
  "name": "New User"
}
```
**Response**:
```json
{
  "message": "User registered successfully",
  "user_id": 123
}
```

### Verify Token

**Endpoint**: `/api/auth/verify`
**Method**: GET
**Description**: Verifies if a token is valid
**Headers**: `Authorization: Bearer <token>`
**Response**:
```json
{
  "valid": true,
  "user_id": 123
}
```

### Refresh Token

**Endpoint**: `/api/auth/refresh`
**Method**: POST
**Description**: Gets a new access token using a refresh token
**Request Body**:
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```
**Response**:
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

## Cart Service

API routes for shopping cart management.

### Get Cart

**Endpoint**: `/api/cart/`
**Method**: GET
**Description**: Returns current cart information
**Headers**: `Authorization: Bearer <token>`
**Response**:
```json
{
  "cart_id": 123,
  "items": [
    {
      "product_id": 456,
      "quantity": 2,
      "price": 19.99,
      "name": "Product Name"
    }
  ],
  "total": 39.98
}
```

### Add to Cart

**Endpoint**: `/api/cart/`
**Method**: POST
**Description**: Adds an item to the cart
**Headers**: `Authorization: Bearer <token>`
**Request Body**:
```json
{
  "product_id": 456,
  "quantity": 1
}
```
**Response**:
```json
{
  "message": "Item added to cart",
  "cart_id": 123,
  "item_id": 789
}
```

## Order Service

API routes for order management.

### Get User Orders

**Endpoint**: `/api/orders/user/{user_id}`
**Method**: GET
**Description**: Gets order history for a user
**Headers**: `Authorization: Bearer <token>`
**Response**:
```json
{
  "orders": [
    {
      "order_id": 123,
      "status": "shipped",
      "total": 59.97,
      "created_at": "2025-05-01T14:30:00Z",
      "items": [
        {
          "product_id": 456,
          "quantity": 3,
          "price": 19.99
        }
      ]
    }
  ]
}
```

### Create Order

**Endpoint**: `/api/orders/`
**Method**: POST
**Description**: Creates a new order from cart
**Headers**: `Authorization: Bearer <token>`
**Request Body**:
```json
{
  "cart_id": 123,
  "shipping_address_id": 456
}
```
**Response**:
```json
{
  "message": "Order created successfully",
  "order_id": 789,
  "status": "processing"
}
```

## Product Service

API routes for product information.

### Get All Products

**Endpoint**: `/api/products/`
**Method**: GET
**Description**: Gets a list of all products
**Response**:
```json
{
  "products": [
    {
      "id": 123,
      "name": "Product Name",
      "price": 19.99,
      "description": "Product description",
      "category": "electronics",
      "image_url": "http://example.com/image.jpg"
    }
  ]
}
```

### Get Product Details

**Endpoint**: `/api/products/{product_id}`
**Method**: GET
**Description**: Gets detailed information about a specific product
**Response**:
```json
{
  "id": 123,
  "name": "Product Name",
  "price": 19.99,
  "description": "Detailed product description",
  "category": "electronics",
  "image_url": "http://example.com/image.jpg",
  "specifications": {
    "weight": "1.5kg",
    "dimensions": "10x15x5cm"
  },
  "reviews": [
    {
      "user_id": 456,
      "rating": 4.5,
      "comment": "Great product"
    }
  ]
}
```

## Profile Service

API routes for user profile management.

### Get User Profile

**Endpoint**: `/api/profiles/profile/{user_id}`
**Method**: GET
**Description**: Gets user profile information
**Headers**: `Authorization: Bearer <token>`
**Response**:
```json
{
  "user_id": 123,
  "name": "User Name",
  "email": "user@example.com",
  "phone": "+1234567890",
  "addresses": [
    {
      "id": 456,
      "street": "123 Main St",
      "city": "Anytown",
      "state": "State",
      "postal_code": "12345",
      "country": "Country",
      "is_default": true
    }
  ]
}
```

### Update Profile

**Endpoint**: `/api/profiles/profile`
**Method**: PATCH
**Description**: Updates user profile information
**Headers**: `Authorization: Bearer <token>`
**Request Body**:
```json
{
  "name": "Updated Name",
  "phone": "+9876543210"
}
```
**Response**:
```json
{
  "message": "Profile updated successfully",
  "user_id": 123
}
```

## Customer Support Service

API routes for customer support.

### Submit Support Request

**Endpoint**: `/api/support/contact`
**Method**: POST
**Description**: Submits a customer support request
**Headers**: `Authorization: Bearer <token>` (optional)
**Request Body**:
```json
{
  "name": "Customer Name",
  "email": "customer@example.com",
  "subject": "Order Problem",
  "message": "I have an issue with my recent order #123"
}
```
**Response**:
```json
{
  "message": "Support request submitted successfully",
  "ticket_id": 789
}
```

## Error Handling

All API endpoints follow a consistent error response format:

```json
{
  "error": "Error type (e.g. Not Found, Unauthorized)",
  "message": "Detailed error message"
}
```

Common HTTP status codes:
- 200: Success
- 201: Created
- 400: Bad Request
- 401: Unauthorized
- 403: Forbidden
- 404: Not Found
- 500: Internal Server Error
