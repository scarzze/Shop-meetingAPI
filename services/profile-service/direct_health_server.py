"""
Direct standalone health check server for the Profile Service.
This is a completely separate Flask application that just runs a health check.
"""
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/health')
def health_check():
    """Simple health check that always returns 200 OK"""
    return jsonify({
        'status': 'healthy',
        'service': 'profile',
        'version': '1.0.0'
    })

if __name__ == '__main__':
    print("Starting direct health check server on port 5013")
    # We're using a different port (5013) so it doesn't conflict with the main app
    app.run(host='0.0.0.0', port=5013, debug=False)
