import os
from app import app

if __name__ == '__main__':
    debug_mode = os.environ.get('DEBUG_MODE', 'false').lower() == 'true'
    app.run(debug=debug_mode, port=5001)
