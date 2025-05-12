# Product Management Microservice

## Overview
The Product Management service is a core microservice responsible for managing the e-commerce platform's product catalog, categories, and reviews. It provides RESTful APIs for creating, reading, updating, and deleting (CRUD) products, categories, and product reviews.

## Features
- Category Management
- Product Management with filtering, pagination and sorting
- Product Review System with ratings

## API Endpoints

### Category Endpoints
- `POST /api/categories` - Create a new category
- `GET /api/categories` - List all categories
- `GET /api/categories/{id}` - Get category details
- `PUT /api/categories/{id}` - Update category
- `DELETE /api/categories/{id}` - Delete category

### Product Endpoints
- `POST /api/products` - Create a new product
- `GET /api/products` - List products (with pagination, filtering, sorting)
- `GET /api/products/{id}` - Get product details
- `PUT /api/products/{id}` - Update product
- `PATCH /api/products/{id}` - Partial update product
- `DELETE /api/products/{id}` - Delete product

### Review Endpoints
- `POST /api/reviews` - Create a new review
- `GET /api/reviews/product/{product_id}` - Get all reviews for a product
- `GET /api/reviews/{id}` - Get review details
- `PUT /api/reviews/{id}` - Update review
- `DELETE /api/reviews/{id}` - Delete review

## Query Parameters for Product Listing
- `page`: Page number for pagination
- `per_page`: Items per page
- `category`: Filter by category name
- `sort`: Sort by field (price, name)
- `order`: Sort order (asc, desc)
- `search`: Search term for product name/description
- `min_price`: Minimum price filter
- `max_price`: Maximum price filter

## Setup and Installation

### Prerequisites
- Python 3.9+
- Flask and related packages (see requirements.txt)

### Development Setup
1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Copy the example environment file and update as needed:
   ```bash
   cp .env.example .env
   ```
5. Run the application:
   ```bash
   python run.py
   ```
6. Seed the database with initial data:
   ```bash
   python seed.py
   ```

### Docker Setup
1. Build and run using Docker Compose:
   ```bash
   docker-compose up --build
   ```

## Authentication
This service integrates with the Auth service for user authentication. Protected endpoints require a valid JWT token in the Authorization header.

## Database Schema

### Category
- id: Integer (Primary Key)
- name: String (Unique)
- description: Text
- created_at: DateTime
- updated_at: DateTime

### Product
- id: Integer (Primary Key)
- name: String
- description: Text
- price: Decimal
- category_id: Integer (Foreign Key to Category)
- stock_quantity: Integer
- sku: String (Unique)
- image_url: String
- created_at: DateTime
- updated_at: DateTime

### Review
- id: Integer (Primary Key)
- product_id: Integer (Foreign Key to Product)
- user_id: String
- user_name: String
- rating: Integer (1-5)
- comment: Text
- created_at: DateTime
- updated_at: DateTime
