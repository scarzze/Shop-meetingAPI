# Shop-meetingAPI Microservices Architecture

This project is a microservices-based e-commerce API that has been transitioned from a monolithic architecture. The application is split into six independent services that communicate with each other via HTTP requests.

## Microservices Overview

1. **Auth Service** (Port 5001)
   - User authentication, registration, login
   - Token management (JWT)
   - Token validation for other services

2. **Profile Service** (Port 5002)
   - User profile management
   - Address book
   - Payment methods

3. **Product Service** (Port 5003)
   - Product catalog
   - Categories
   - Reviews
   - Favorites/Wishlist
   - Search functionality

4. **Cart Service** (Port 5004)
   - Shopping cart management
   - Add/remove/update cart items

5. **Order Service** (Port 5005)
   - Order processing
   - Order history
   - Payment processing

6. **Customer Support Service** (Port 5006)
   - Support tickets
   - Messaging
   - Real-time chat (Socket.IO)

7. **API Gateway** (Port 5000)
   - Single entry point for clients
   - Request routing to appropriate services

## Project Structure

```
Shop-meetingAPI/
├── api-gateway/                  # API Gateway service
│   ├── app.py                    # Main application file
│   ├── Dockerfile                # Docker configuration
│   ├── requirements.txt          # Dependencies
│   └── .env                      # Environment variables
├── services/
│   ├── auth-service/             # Authentication service
│   │   ├── app.py                # Main application file
│   │   ├── models.py             # Data models
│   │   ├── seed.py               # Seed data
│   │   ├── Dockerfile            # Docker configuration
│   │   ├── requirements.txt      # Dependencies
│   │   └── .env                  # Environment variables
│   ├── profile-service/          # User profile service
│   ├── product-service/          # Product catalog service
│   ├── cart-service/             # Shopping cart service
│   ├── order-service/            # Order processing service
│   └── customer-support-service/ # Customer support service
├── docker-compose.yml            # Docker Compose configuration
├── run_services.sh               # Script to run all services
├── install_dependencies.sh       # Script to install dependencies
└── README.md                     # Project documentation
```

## Getting Started

### Prerequisites

- Python 3.9+
- pip
- virtualenv (optional)
- Docker and Docker Compose (optional, for containerized deployment)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/Shop-meetingAPI.git
   cd Shop-meetingAPI
   ```

2. Install dependencies:
   ```bash
   # Make the script executable
   chmod +x install_dependencies.sh
   
   # Run the script to install dependencies
   ./install_dependencies.sh
   ```

3. Set up environment variables:
   - Each service has its own `.env` file with configuration settings
   - Update the values as needed for your environment

### Database Setup and Seeding

Before running the services, you need to set up and seed the databases with initial test data:

```bash
# Make the script executable
chmod +x seed_all.sh

# Seed all databases
./seed_all.sh
```

This will create the necessary database files and populate them with test data, including:
- Test users (alice/password123, bob/password123)
- Sample products
- User profiles
- Sample orders
- Test support tickets

### Running the Services

#### Option 1: Using the start_all.sh script (Recommended)

This script starts all services, the API Gateway, and the frontend in one command:

```bash
# Make the script executable
chmod +x start_all.sh

# Start everything
./start_all.sh

# When you're done, stop everything
./stop_all.sh
```

#### Option 2: Using the run_services.sh script

```bash
# Make the script executable
chmod +x run_services.sh

# Start all services
./run_services.sh start

# Check status of services
./run_services.sh status

# Stop all services
./run_services.sh stop

# Restart all services
./run_services.sh restart
```

Then start the API Gateway and frontend separately:

```bash
# Start API Gateway
cd api-gateway
python app.py
```

#### Option 3: Using Docker Compose

```bash
# Build and start all services
docker-compose up --build

# Run in detached mode
docker-compose up -d

# Stop all services
docker-compose down
```

#### Option 4: Running services individually

Start each service in a separate terminal:

```bash
# Auth Service
cd services/auth-service
python app.py

# Profile Service
cd services/profile-service
python app.py

# Product Service
cd services/product-service
python app.py

# Cart Service
cd services/cart-service
python app.py

# Order Service
cd services/order-service
python app.py

# Customer Support Service
cd services/customer-support-service
python app.py

# API Gateway
cd api-gateway
python app.py
```

## API Endpoints

### Auth Service (http://localhost:5001)
- `POST /register` - Register a new user
- `POST /login` - User login
- `POST /logout` - User logout
- `POST /refresh` - Refresh access token
- `POST /validate` - Validate token (internal use)

### Profile Service (http://localhost:5002)
- `GET /profile` - Get user profile
- `PUT /profile` - Update user profile
- `GET /payment-methods` - Get user payment methods
- `POST /payment-methods` - Add payment method
- `DELETE /payment-methods/<payment_id>` - Delete payment method

### Product Service (http://localhost:5003)
- `GET /products` - Get all products
- `GET /products/<product_id>` - Get product by ID
- `GET /categories/<category>` - Get products by category
- `POST /products/<product_id>/reviews` - Add review
- `GET /products/<product_id>/reviews` - Get reviews for a product
- `GET /favorites` - Get user's wishlist/favorites
- `POST /favorites` - Add to wishlist
- `DELETE /favorites/<product_id>` - Remove from wishlist
- `GET /search` - Search products

### Cart Service (http://localhost:5004)
- `GET /cart` - Get cart
- `POST /cart/items` - Add or update cart item
- `PUT /cart/items/<item_id>` - Update cart item quantity
- `DELETE /cart/items/<item_id>` - Remove item from cart
- `DELETE /cart` - Clear cart

### Order Service (http://localhost:5005)
- `POST /orders` - Create order (checkout)
- `GET /orders` - Get user orders
- `GET /orders/<order_id>` - Get order details
- `PUT /orders/<order_id>` - Update order status
- `DELETE /orders/<order_id>/cancel` - Cancel order

### Customer Support Service (http://localhost:5006)
- `POST /tickets` - Create support ticket
- `GET /tickets` - Get user tickets
- `GET /tickets/<ticket_id>` - Get ticket details
- `POST /tickets/<ticket_id>/messages` - Add message to ticket
- `PUT /tickets/<ticket_id>/close` - Close ticket

### API Gateway (http://localhost:5000)
- Routes all requests to the appropriate service
- Provides a single entry point for clients

## Testing

### Seeding Test Data

Each service includes seed data for testing purposes. You can seed all databases at once or individual services:

```bash
# Seed all databases at once
./seed_all.sh

# Or seed individual services
cd services/<service-name>
python seed.py
```

### Automated Testing

The project includes a test script to verify all services are working correctly:

```bash
# Make the script executable
chmod +x test_services.py

# Run the tests
./test_services.py
```

This script will test each service endpoint and verify that they can communicate with each other properly.

## Inter-Service Communication

Services communicate with each other via HTTP requests. For example:
- Auth Service validates tokens for other services
- Order Service communicates with Cart Service to get cart items
- Order Service communicates with Profile Service to get payment methods

## Security

- JWT tokens are used for authentication
- CORS is configured to restrict access to specified origins
- Environment variables are used for sensitive configuration

## Next Steps

1. **Implement more robust error handling**
   - Add global error handlers for each service
   - Implement consistent error response formats
   - Add retry mechanisms for inter-service communication

2. **Add logging and monitoring**
   - Use the logging-service to centralize logs from all services
   - Implement health check endpoints for each service
   - Add performance metrics collection
   - Set up alerts for critical errors

3. **Implement message queues for asynchronous communication**
   - Replace direct HTTP calls with message queues (RabbitMQ/Kafka)
   - Implement event-driven architecture for better scalability
   - Add retry mechanisms for failed messages

4. **Set up CI/CD pipeline**
   - Implement automated testing in CI pipeline
   - Set up containerized deployments
   - Implement blue/green deployment strategy

5. **Add unit and integration tests**
   - Expand the test_services.py script with more test cases
   - Add unit tests for each service
   - Implement integration tests for service interactions

6. **Implement rate limiting and API throttling**
   - Add rate limiting to the API Gateway
   - Implement token bucket algorithm for throttling
   - Add user-specific rate limits

## License

This project is licensed under the MIT License - see the LICENSE file for details.
