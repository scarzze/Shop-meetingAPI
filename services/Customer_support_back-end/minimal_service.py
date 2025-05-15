from flask import Flask, jsonify

# Create the simplest possible Flask app
app = Flask(__name__)

# Simple health check endpoint
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'service': 'customer-support'
    })

# Root endpoint
@app.route('/')
def index():
    return jsonify({
        'message': 'Customer Support Service is running'
    })

if __name__ == '__main__':
    # Run on port 5004 with debug enabled
    print("Starting minimal Customer Support Service on port 5004")
    app.run(host='0.0.0.0', port=5004, debug=True)
