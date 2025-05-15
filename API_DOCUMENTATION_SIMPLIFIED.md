# Shop-meetingAPI Documentation

## Overview

Shop-meetingAPI provides standardized access to e-commerce microservices through a Docker-based Nginx API Gateway.

## API Gateway

- **Base URL**: `http://localhost:8080`
- **Configuration**: Docker container with Nginx routing
- **Health Check**: `http://localhost:8080/api/health`

## Microservices Architecture

| Service | Port | Endpoint Prefix | Function |
|---------|------|-----------------|----------|
| Auth | 5002 | `/api/v1/auth/` | Authentication and user management |
| Profile | 5003 | `/api/v1/profiles/` | User profiles and preferences |
| Cart | 5001 | `/api/v1/carts/` | Shopping cart functionality |
| Order | 5005 | `/api/v1/orders/` | Order processing and tracking |
| Customer Support | 5004 | `/api/v1/tickets/` | Support tickets and chat |
| Product | 5006 | `/api/v1/products/` | Product catalog and inventory |

## Starting the System

```bash
# Start all microservices
python manage_services.py start --all --debug

# Start the API Gateway
docker-compose up -d

# Verify health
curl http://localhost:8080/api/health
```

## Authentication

All protected endpoints require a JWT token in the Authorization header:

```
Authorization: Bearer {token}
```

### Login

```
POST http://localhost:8080/api/v1/auth/login

{
  "email": "user@example.com",
  "password": "securepassword"
}
```

## Frontend Integration Examples

### Authentication Flow

```javascript
// Login and get token
fetch('http://localhost:8080/api/v1/auth/login', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    email: 'user@example.com',
    password: 'securepassword'
  })
})
.then(response => response.json())
.then(data => {
  localStorage.setItem('auth_token', data.access_token);
});

// Making authenticated requests
const token = localStorage.getItem('auth_token');

fetch('http://localhost:8080/api/v1/profiles/1', {
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  }
})
.then(response => response.json())
.then(data => console.log(data));
```

### Health Check Integration

```javascript
fetch('http://localhost:8080/api/health')
  .then(response => response.json())
  .then(data => {
    const allServicesUp = Object.values(data.services).every(status => status === 'UP');
    console.log(`All services healthy: ${allServicesUp}`);
  });
```

### Shopping Flow Example

```javascript
// 1. Fetch products
fetch('http://localhost:8080/api/v1/products?page=1')
  .then(response => response.json())
  .then(data => {
    const productId = data.products[0].id;
    return productId;
  })
  .then(productId => {
    // 2. Add to cart
    return fetch('http://localhost:8080/api/v1/carts/items', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        product_id: productId,
        quantity: 1
      })
    });
  })
  .then(response => response.json())
  .then(cartData => {
    // 3. Create order
    return fetch('http://localhost:8080/api/v1/orders', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        shipping_address_id: 1,
        payment_method: 'credit_card',
        payment_details: {
          card_number: '************1234',
          expiry_date: '12/26',
          card_holder: 'John Doe'
        }
      })
    });
  })
  .then(response => response.json())
  .then(orderData => {
    console.log('Order created:', orderData);
  });
```

## CORS Settings

The API Gateway allows cross-origin requests from any origin with the following headers:

```
Access-Control-Allow-Origin: *
Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS
Access-Control-Allow-Headers: DNT, User-Agent, X-Requested-With, If-Modified-Since, Cache-Control, Content-Type, Range, Authorization
```

## Error Responses

All API endpoints return a standardized error format:

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Error description",
    "details": "Additional details"
  }
}
```

Common status codes: 200 (OK), 201 (Created), 400 (Bad Request), 401 (Unauthorized), 403 (Forbidden), 404 (Not Found), 500 (Server Error)
