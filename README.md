# Shop Meeting API Microservices

This project consists of multiple microservices that work together to provide a complete e-commerce platform API.

## Services

- Auth Service (Port 5002): Handles user authentication and authorization
- Cart Service (Port 5001): Manages shopping cart operations
- Profile Service (Port 5003): Manages user profiles and preferences
- Order Service (Port 5005): Handles order processing and management
- Customer Support Service (Port 5004): Provides customer support functionality

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

The services will be available at:
- Auth Service: http://localhost:5002
- Cart Service: http://localhost:5001
- Profile Service: http://localhost:5003
- Order Service: http://localhost:5005
- Customer Support: http://localhost:5004

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

2. If services can't communicate:
   - Verify all services are running
   - Check the health status
   - Verify network configuration in docker-compose.yml

3. For authentication issues:
   - Verify Auth Service is running
   - Check JWT token configuration
   - Verify service URLs in environment variables