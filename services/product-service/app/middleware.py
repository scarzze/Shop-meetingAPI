class CORSMiddleware:
    """Middleware to handle CORS requests"""

    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        def custom_start_response(status, headers, exc_info=None):
            # Add CORS headers to every response
            cors_headers = [
                ('Access-Control-Allow-Origin', '*'),
                ('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS'),
                ('Access-Control-Allow-Headers', 'Content-Type, Authorization'),
                ('Access-Control-Allow-Credentials', 'true')
            ]
            
            # Add CORS headers to the existing headers
            headers_with_cors = list(headers) + cors_headers
            
            return start_response(status, headers_with_cors, exc_info)
        
        # Handle OPTIONS request directly
        if environ['REQUEST_METHOD'] == 'OPTIONS':
            # Return 200 OK with CORS headers for preflight requests
            return custom_start_response('200 OK', [('Content-Type', 'text/plain')])([b''])
            
        return self.app(environ, custom_start_response)
