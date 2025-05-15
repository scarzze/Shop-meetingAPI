from flask import Flask, jsonify

# Create a minimal Flask app
app = Flask(__name__)

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'healthy',
        'service': 'product',
        'message': 'Product Service is operational'
    })

@app.route('/', methods=['GET'])
def root():
    return jsonify({
        'message': 'Product Service root endpoint'
    })

if __name__ == '__main__':
    try:
        print("Starting minimal Product Service on port 5006")
        # Run on port 5006 without debug mode for stability
        app.run(host='0.0.0.0', port=5006, debug=False)
    except Exception as e:
        print(f"Error starting service: {e}")
