# Nginx API Gateway Setup

This document explains how to use the Nginx API Gateway for the Shop-meetingAPI.

## Overview

The API Gateway serves as a unified entry point for all microservices. It handles:
- Routing requests to the appropriate services
- Managing CORS for frontend integration
- Providing health check endpoints

## Setup Instructions

### Windows Setup

1. Download Nginx for Windows from https://nginx.org/en/download.html
2. Extract to a location of your choice (e.g., `C:\nginx`)
3. Copy the `shop_api.conf` file to the Nginx directory
4. Start Nginx with the custom configuration:

```powershell
# Navigate to your Nginx install directory
cd C:\path\to\nginx

# Start Nginx with our configuration
.\nginx.exe -c "path\to\shop_api.conf"
```

### Ubuntu Setup

1. Install Nginx:
```bash
sudo apt update
sudo apt install nginx
```

2. Copy the configuration file:
```bash
sudo cp ./nginx/shop_api.conf /etc/nginx/sites-available/shop-api
```

3. Create a symbolic link to enable the site:
```bash
sudo ln -s /etc/nginx/sites-available/shop-api /etc/nginx/sites-enabled/
```

4. Restart Nginx:
```bash
sudo systemctl restart nginx
```

## Accessing the API

The API Gateway runs on port 9000:

- API Base URL: `http://localhost:9000/api/v1`
- Health Check: `http://localhost:9000/api/v1/health`

## Service Endpoints

- Auth Service: `/api/v1/auth/...`
- Profile Service: `/api/v1/profile/...`
- Cart Service: `/api/v1/cart/...`
- Order Service: `/api/v1/order/...`
- Customer Support: `/api/v1/customer-support/...`
- Product Service: `/api/v1/product/...`

## Troubleshooting

If you encounter issues with the API Gateway:

1. Ensure all microservices are running:
   ```bash
   python manage_services.py check
   ```

2. Check Nginx logs for errors:
   - Windows: Check the logs directory in your Nginx installation
   - Ubuntu: Check `/var/log/nginx/error.log`

3. Verify no port conflicts:
   ```bash
   # On Ubuntu
   sudo netstat -tulpn | grep 9000
   
   # On Windows
   netstat -ano | findstr :9000
   ```
