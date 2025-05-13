from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Configure CORS
allowed_origins = ["http://127.0.0.1:5173", "http://localhost:5173", "http://localhost:3000"]
frontend_url = os.getenv('FRONTEND_URL')
if frontend_url and frontend_url not in allowed_origins:
    allowed_origins.append(frontend_url)

CORS(app, 
     resources={r"/*": {
         "origins": allowed_origins,
         "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
         "allow_headers": ["Content-Type", "Authorization", "X-Requested-With"],
         "supports_credentials": True,
         "expose_headers": ["Authorization"]
     }},
     supports_credentials=True,
     allow_credentials=True
)

# Service URLs
AUTH_SERVICE_URL = os.getenv('AUTH_SERVICE_URL', 'http://localhost:5001')
PROFILE_SERVICE_URL = os.getenv('PROFILE_SERVICE_URL', 'http://localhost:5002')
PRODUCT_SERVICE_URL = os.getenv('PRODUCT_SERVICE_URL', 'http://localhost:5003')
CART_SERVICE_URL = os.getenv('CART_SERVICE_URL', 'http://localhost:5004')
ORDER_SERVICE_URL = os.getenv('ORDER_SERVICE_URL', 'http://localhost:5005')
SUPPORT_SERVICE_URL = os.getenv('SUPPORT_SERVICE_URL', 'http://localhost:5006')

# Service route prefixes
SERVICE_ROUTES = {
    '/auth': AUTH_SERVICE_URL,
    '/profile': PROFILE_SERVICE_URL,
    '/products': PRODUCT_SERVICE_URL,
    '/categories': PRODUCT_SERVICE_URL,
    '/search': PRODUCT_SERVICE_URL,
    '/favorites': PRODUCT_SERVICE_URL,
    '/recommendations': PRODUCT_SERVICE_URL,
    '/cart': CART_SERVICE_URL,
    '/orders': ORDER_SERVICE_URL,
    '/tickets': SUPPORT_SERVICE_URL,
}

@app.route('/')
def index():
    return jsonify({
        'message': 'Shop Meeting API Gateway',
        'services': {
            'auth': AUTH_SERVICE_URL,
            'profile': PROFILE_SERVICE_URL,
            'products': PRODUCT_SERVICE_URL,
            'cart': CART_SERVICE_URL,
            'orders': ORDER_SERVICE_URL,
            'support': SUPPORT_SERVICE_URL
        }
    })

@app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])
def proxy(path):
    # Find the appropriate service for the requested path
    service_url = None
    for prefix, url in SERVICE_ROUTES.items():
        if path.startswith(prefix.lstrip('/')):
            service_url = url
            break
    
    # If no service found, return 404
    if not service_url:
        return jsonify({'error': 'Service not found'}), 404
    
    # Forward the request to the appropriate service
    target_url = f"{service_url}/{path}"
    
    # Copy request headers
    headers = {key: value for key, value in request.headers if key != 'Host'}
    
    # Forward the request
    try:
        resp = requests.request(
            method=request.method,
            url=target_url,
            headers=headers,
            params=request.args,
            data=request.get_data(),
            cookies=request.cookies,
            allow_redirects=False
        )
        
        # Create Flask response
        response = Response(
            resp.content,
            status=resp.status_code,
            content_type=resp.headers.get('Content-Type', 'application/json')
        )
        
        # Copy response headers
        for key, value in resp.headers.items():
            if key.lower() not in ('content-length', 'connection', 'content-encoding'):
                response.headers[key] = value
        
        return response
    except requests.exceptions.RequestException as e:
        return jsonify({'error': f'Service unavailable: {str(e)}'}), 503

# Special routes for authentication
@app.route('/register', methods=['POST'])
def register():
    return proxy('auth/register')

@app.route('/login', methods=['POST'])
def login():
    return proxy('auth/login')

@app.route('/logout', methods=['POST'])
def logout():
    return proxy('auth/logout')

@app.route('/refresh', methods=['POST'])
def refresh():
    return proxy('auth/refresh')

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
