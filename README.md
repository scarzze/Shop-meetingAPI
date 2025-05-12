# Shop Meeting API Microservices

This project consists of multiple microservices that work together to provide a complete e-commerce platform API.

## Services

- Auth Service (Port 5002): Handles user authentication and authorization
- Cart Service (Port 5001): Manages shopping cart operations
- Profile Service (Port 5003): Manages user profiles and preferences
- Order Service (Port 5005): Handles order processing and management
- Customer Support Service (Port 5004): Provides customer support functionality with WebSocket support for real-time chat
- Product Management Service (Port 5006): Manages products, categories, and reviews

## API Gateway

An Nginx-based API gateway is configured to route requests to the appropriate services:

- `/api/auth/` → Auth Service
- `/api/cart/` → Cart Service
- `/api/products/` → Product Service
- `/api/orders/` → Order Service
- `/api/profiles/` → Profile Service
- `/api/support/` → Customer Support Service

## Prerequisites

- Docker and Docker Compose
- PostgreSQL
- Python 3.8 or higher

## Setup Instructions

1. Make the database initialization script executable:
```bash
chmod +x init_databases.sh
```

2. Initialize the databases:
```bash
./init_databases.sh
```

3. Start all services using Docker Compose:
```bash
docker-compose up --build
```

4. Alternatively, use the service management scripts:
```bash
# Using the Python script
python manage_services.py start    # Start all services
python manage_services.py check   # Check the health of all services
python manage_services.py debug   # Start services in debug mode
python manage_services.py prod    # Start services in production mode

# Using the Shell script (make executable first: chmod +x manage_services.sh)
./manage_services.sh start       # Start all services
./manage_services.sh restart     # Restart all services
./manage_services.sh check       # Check the health of all services
./manage_services.sh debug       # Start services in debug mode
./manage_services.sh prod        # Start services in production mode

# You can also target specific services:
./manage_services.sh restart cart-service   # Restart only the cart service
```

The services will be available at:
- Auth Service: http://localhost:5002
- Cart Service: http://localhost:5001
- Profile Service: http://localhost:5003
- Order Service: http://localhost:5005
- Customer Support: http://localhost:5004
- Product Management Service: http://localhost:5006

## Health Monitoring

The health checker service will automatically monitor all services and provide status updates. You can check the current status in the `health_status.json` file or by checking the health checker service logs:

```bash
docker-compose logs -f health-checker
```

## Service Dependencies

- All services depend on the Auth Service for user authentication
- All services require PostgreSQL database access
- Services communicate with each other using REST APIs

## Environment Variables

Each service uses environment variables for configuration. These are set in the docker-compose.yml file, but you can override them by creating a .env file in each service directory.

## API Documentation

Each service provides a /health endpoint that returns its current status.

Common endpoints across services:
- POST /auth/login (Auth Service)
- POST /auth/register (Auth Service)
- GET /cart (Cart Service)
- GET /profile (Profile Service)
- POST /orders (Order Service)
- POST /support/tickets (Customer Support)

For detailed API documentation, refer to each service's individual README file.

## Development

To run services individually for development:

1. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run a service (example with auth service):
```bash
cd services/auth-service
python run.py
```

## Testing

Each service has its own test suite. To run tests:

```bash
# For each service directory
python -m pytest
```

## Troubleshooting

1. If services can't connect to the database:
   - Verify PostgreSQL is running
   - Check database credentials in .env files
   - Run init_databases.sh script
   - Make sure environment variable names are correct (Cart Service uses DATABASE_URI, not DATABASE_URL)
   - Make sure Customer Support Service uses DATABASE_URI, not DATABASE_URL

2. If services can't communicate:
   - Verify all services are running
   - Check the health status
   - Verify network configuration in docker-compose.yml
   - Ensure nginx.conf has correct service port mappings (Profile Service runs on port 5003, not 5000)

3. For authentication issues:
   - Verify Auth Service is running
   - Check JWT token configuration
   - Verify service URLs in environment variables

4. Common service-specific issues:
   - Cart Service requires DATABASE_URI in .env and docker-compose.yml
   - Customer Support Service requires DATABASE_URI in .env and docker-compose.yml
   - Profile Service runs on port 5003, make sure nginx.conf reflects this

## Recent Fixes Applied

1. Fixed environment variable names in docker-compose.yml:
   - Changed Cart Service environment variable from DATABASE_URL to DATABASE_URI
   - Changed Customer Support Service environment variable from DATABASE_URL to DATABASE_URI

2. Fixed Profile Service port in nginx.conf (changed from 5000 to 5003)

3. Added manage_services.sh shell script to provide a convenient way to start, restart, and check services