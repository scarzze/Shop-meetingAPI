# Shop-meetingAPI

A comprehensive microservices-based e-commerce API system with Docker support and React integration capabilities.

## Architecture

The system consists of 6 microservices:

1. **Auth Service** (port 5002): Handles user authentication and authorization
2. **Profile Service** (port 5003): Manages user profiles and preferences
3. **Cart Service** (port 5001): Handles shopping cart operations
4. **Order Service** (port 5005): Manages order creation and fulfillment
5. **Customer Support Service** (port 5004): Handles customer tickets and support
6. **Product Service** (port 5006): Manages product catalog and inventory

All services are fronted by an Nginx API Gateway that provides standardized endpoints and handles cross-origin requests.

## Getting Started

### Prerequisites

- Python 3.8+ (for local development)
- Docker and Docker Compose (for containerized deployment)
- PostgreSQL (for production database) or SQLite (for development)

### Setup for Development

#### Ubuntu/Linux

```bash
# Install required packages
sudo apt update
sudo apt install python3 python3-pip python3-venv postgresql

# Clone the repository
git clone https://github.com/your-org/Shop-meetingAPI.git
cd Shop-meetingAPI

# Start all services in debug mode with local database
python3 manage_services.py debug --local-db
```

#### Windows

```powershell
# Clone the repository
git clone https://github.com/your-org/Shop-meetingAPI.git
cd Shop-meetingAPI

# Start all services in debug mode with local database
python manage_services.py debug --local-db
```

### Docker Deployment

```bash
# Build and start all services using Docker Compose
docker-compose up --build
```

## Service Management

The `manage_services.py` script provides several options for managing services:

- `python manage_services.py start`: Start all services in production mode
- `python manage_services.py debug`: Start all services in debug mode
- `python manage_services.py check`: Check the health of all services

To manage a specific service:

```bash
python manage_services.py debug --service "Auth Service" --local-db
```

## API Gateway

The Nginx API gateway provides the following standardized endpoints:

- Auth: `/api/v1/auth/*`
- Profiles: `/api/v1/profiles/*`
- Carts: `/api/v1/carts/*`
- Orders: `/api/v1/orders/*` 
- Products: `/api/v1/products/*`
- Customer Support: `/api/v1/tickets/*`

All health checks are available at `/api/v1/{service-name}/health`

## Frontend Integration

The backend is configured for seamless integration with React frontends. CORS headers are properly set to allow cross-origin requests from your frontend application.

### React Integration Example

```javascript
// API client for React
const API_BASE = 'http://localhost:8080/api/v1';

export const api = {
  // Auth
  login: (credentials) => (
    fetch(`${API_BASE}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(credentials)
    }).then(res => res.json())
  ),
  
  // Products
  getProducts: () => (
    fetch(`${API_BASE}/products`, {
      headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
    }).then(res => res.json())
  ),
  
  // Other API calls...
}

## Package Descriptions for profile service
Package	Purpose
Flask	Core web framework
Flask-Cors	Enable CORS for cross-origin requests
Flask-SQLAlchemy	ORM for working with PostgreSQL
psycopg2-binary	PostgreSQL driver
python-dotenv	Load environment variables from .env file
PyJWT	JSON Web Token encoding/decoding
requests	Send HTTP requests (e.g., calling other services)
python-dateutil	Better date handling (timestamps, etc.)

## Troubleshooting

### Service Health Checks

If services are not responding to health checks:

1. Check if all required environment variables are set
2. Verify database connections are working
3. Check network connectivity between services
4. Increase health check timeouts with the `--timeout` option

### WSL2 vs Windows Differences

If you're experiencing different behavior when running services in WSL2 vs Windows:

1. Use `python manage_services.py debug --local-db` which is configured to work in both environments
2. WSL2 may require longer timeouts for health checks
3. Network routing between WSL2 and Windows can cause connectivity issues

## License

MIT
