from flask import Flask

app = Flask(__name__)

@app.route('/health')
def health():
    return {'status': 'healthy', 'service': 'customer-support'}

if __name__ == '__main__':
    print('Starting Customer Support Service on alternative port 5014')
    app.run(host='0.0.0.0', port=5014)
