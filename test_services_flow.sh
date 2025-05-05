#!/bin/bash
# A script to demonstrate the full user flow across all microservices
# including the new Product Management service

echo "=== Starting Shop Meeting API Test Flow ==="
echo ""

# Set base URLs for all services
AUTH_SERVICE="http://localhost:5002"
CART_SERVICE="http://localhost:5001"
PROFILE_SERVICE="http://localhost:5003"
ORDER_SERVICE="http://localhost:5005"
SUPPORT_SERVICE="http://localhost:5004"
PRODUCT_SERVICE="http://localhost:5006"

# Colors for better readability
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Step 1: User Registration (if needed)
echo -e "${BLUE}=== Step 1: User Registration ===${NC}"
echo "Registering a new test user (if needed)..."
REGISTER_RESPONSE=$(curl -s -X POST "$AUTH_SERVICE/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"email":"testuser@example.com","password":"password123","first_name":"Test","last_name":"User"}')

# Check if user already exists or was created
if [[ "$REGISTER_RESPONSE" == *"User already exists"* ]]; then
  echo -e "${YELLOW}User already exists. Proceeding to login.${NC}"
else
  echo -e "${GREEN}User registered successfully!${NC}"
  echo "$REGISTER_RESPONSE"
fi
echo ""

# Step 2: User Login
echo -e "${BLUE}=== Step 2: User Login ===${NC}"
echo "Logging in as testuser@example.com..."
LOGIN_RESPONSE=$(curl -s -X POST "$AUTH_SERVICE/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"testuser@example.com","password":"password123"}')

# Extract token from login response
TOKEN=$(echo $LOGIN_RESPONSE | grep -o '"token":"[^"]*' | sed 's/"token":"//')

if [ -z "$TOKEN" ]; then
  echo -e "${RED}Login failed! Couldn't get auth token.${NC}"
  echo "Response: $LOGIN_RESPONSE"
  exit 1
else
  echo -e "${GREEN}Login successful! Received authentication token.${NC}"
  echo "Token: $TOKEN (truncated for display)"
fi
echo ""

# Save token to environment variable
export AUTH_TOKEN="Bearer $TOKEN"

# Step 3: Access User Profile
echo -e "${BLUE}=== Step 3: Access User Profile ===${NC}"
echo "Fetching user profile data..."
PROFILE_RESPONSE=$(curl -s -X GET "$PROFILE_SERVICE/api/profile/" \
  -H "Authorization: $AUTH_TOKEN")

echo -e "${GREEN}Profile data:${NC}"
echo "$PROFILE_RESPONSE"
echo ""

# Step 4: View User's Cart
echo -e "${BLUE}=== Step 4: View User's Cart ===${NC}"
echo "Fetching shopping cart contents..."
CART_RESPONSE=$(curl -s -X GET "$CART_SERVICE/api/cart/" \
  -H "Authorization: $AUTH_TOKEN")

echo -e "${GREEN}Cart data:${NC}"
echo "$CART_RESPONSE"
echo ""

# Step 5: Work with Product Categories
echo -e "${BLUE}=== Step 5: Product Management - Categories ===${NC}"
echo "Fetching product categories..."
CATEGORIES_RESPONSE=$(curl -s -X GET "$PRODUCT_SERVICE/api/categories")

echo -e "${GREEN}Categories:${NC}"
echo "$CATEGORIES_RESPONSE"
echo ""

# Step 6: Create a new category (requires authentication)
echo -e "${BLUE}=== Step 6: Create a New Product Category ===${NC}"
echo "Creating a new category 'Test Category'..."
CREATE_CATEGORY_RESPONSE=$(curl -s -X POST "$PRODUCT_SERVICE/api/categories" \
  -H "Authorization: $AUTH_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"Test Category","description":"A test category created via API"}')

echo -e "${GREEN}New category created:${NC}"
echo "$CREATE_CATEGORY_RESPONSE"
echo ""

# Extract the category ID from the response
CATEGORY_ID=$(echo $CREATE_CATEGORY_RESPONSE | grep -o '"id":[0-9]*' | head -1 | sed 's/"id"://')

# Step 7: View Products
echo -e "${BLUE}=== Step 7: View Products ===${NC}"
echo "Fetching products with pagination and filtering..."
PRODUCTS_RESPONSE=$(curl -s -X GET "$PRODUCT_SERVICE/api/products?page=1&per_page=5")

echo -e "${GREEN}Products:${NC}"
echo "$PRODUCTS_RESPONSE"
echo ""

# Step 8: Create a New Product
echo -e "${BLUE}=== Step 8: Create a New Product ===${NC}"
echo "Creating a new product in the test category..."
CREATE_PRODUCT_RESPONSE=$(curl -s -X POST "$PRODUCT_SERVICE/api/products" \
  -H "Authorization: $AUTH_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"name\":\"Test Product\",\"description\":\"A test product created via API\",\"price\":99.99,\"category_id\":$CATEGORY_ID,\"stock_quantity\":100,\"sku\":\"TEST-001\"}")

echo -e "${GREEN}New product created:${NC}"
echo "$CREATE_PRODUCT_RESPONSE"
echo ""

# Extract the product ID from the response
PRODUCT_ID=$(echo $CREATE_PRODUCT_RESPONSE | grep -o '"id":[0-9]*' | head -1 | sed 's/"id"://')

# Step 9: Add a Review for the Product
echo -e "${BLUE}=== Step 9: Add a Product Review ===${NC}"
echo "Adding a review for the new product..."
ADD_REVIEW_RESPONSE=$(curl -s -X POST "$PRODUCT_SERVICE/api/reviews" \
  -H "Authorization: $AUTH_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"product_id\":$PRODUCT_ID,\"user_name\":\"Test User\",\"rating\":5,\"comment\":\"This is an excellent product!\"}")

echo -e "${GREEN}Review added:${NC}"
echo "$ADD_REVIEW_RESPONSE"
echo ""

# Step 10: Get Reviews for the Product
echo -e "${BLUE}=== Step 10: Get Product Reviews ===${NC}"
echo "Fetching reviews for the product..."
REVIEWS_RESPONSE=$(curl -s -X GET "$PRODUCT_SERVICE/api/reviews/product/$PRODUCT_ID")

echo -e "${GREEN}Product reviews:${NC}"
echo "$REVIEWS_RESPONSE"
echo ""

# Step 11: Add product to cart
echo -e "${BLUE}=== Step 11: Add Product to Cart ===${NC}"
echo "Adding the new product to the shopping cart..."
ADD_TO_CART_RESPONSE=$(curl -s -X POST "$CART_SERVICE/api/cart/add" \
  -H "Authorization: $AUTH_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"product_id\":\"$PRODUCT_ID\",\"quantity\":2}")

echo -e "${GREEN}Add to cart response:${NC}"
echo "$ADD_TO_CART_RESPONSE"
echo ""

# Step 12: View updated cart
echo -e "${BLUE}=== Step 12: View Updated Cart ===${NC}"
echo "Fetching updated shopping cart contents..."
UPDATED_CART_RESPONSE=$(curl -s -X GET "$CART_SERVICE/api/cart/" \
  -H "Authorization: $AUTH_TOKEN")

echo -e "${GREEN}Updated cart data:${NC}"
echo "$UPDATED_CART_RESPONSE"
echo ""

# Step 13: Create a support ticket
echo -e "${BLUE}=== Step 13: Create a Support Ticket ===${NC}"
echo "Creating a customer support ticket..."
TICKET_RESPONSE=$(curl -s -X POST "$SUPPORT_SERVICE/api/tickets" \
  -H "Authorization: $AUTH_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"subject\":\"Question about Test Product\",\"message\":\"I have a question about the Test Product I just purchased.\",\"priority\":\"medium\"}")

echo -e "${GREEN}Support ticket created:${NC}"
echo "$TICKET_RESPONSE"
echo ""

# Step 14: Clean up - Delete the test product
echo -e "${BLUE}=== Step 14: Clean Up - Delete Test Product ===${NC}"
echo "Deleting the test product..."
DELETE_PRODUCT_RESPONSE=$(curl -s -X DELETE "$PRODUCT_SERVICE/api/products/$PRODUCT_ID" \
  -H "Authorization: $AUTH_TOKEN")

echo -e "${GREEN}Delete product response:${NC}"
echo "$DELETE_PRODUCT_RESPONSE"
echo ""

# Step 15: Clean up - Delete the test category
echo -e "${BLUE}=== Step 15: Clean Up - Delete Test Category ===${NC}"
echo "Deleting the test category..."
DELETE_CATEGORY_RESPONSE=$(curl -s -X DELETE "$PRODUCT_SERVICE/api/categories/$CATEGORY_ID" \
  -H "Authorization: $AUTH_TOKEN")

echo -e "${GREEN}Delete category response:${NC}"
echo "$DELETE_CATEGORY_RESPONSE"
echo ""

echo -e "${BLUE}=== End of Test Flow ===${NC}"
echo "The test has completed, demonstrating the full flow across all microservices."
echo "The services continue to run and are available for further testing."
