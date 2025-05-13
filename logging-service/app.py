from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import json
import logging
from datetime import datetime
import threading
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
         "methods": ["GET", "POST", "OPTIONS"],
         "allow_headers": ["Content-Type", "Authorization", "X-Requested-With"],
     }}
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/logging_service.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# In-memory log storage (for demo purposes)
# In a production environment, you would use a database
logs = []
logs_lock = threading.Lock()

@app.route('/')
def index():
    return jsonify({
        'message': 'Logging Service',
        'status': 'running',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/logs', methods=['POST'])
def collect_logs():
    data = request.json
    
    if not data:
        return jsonify({'error': 'No log data provided'}), 400
    
    required_fields = ['service', 'level', 'message']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    # Add timestamp if not provided
    if 'timestamp' not in data:
        data['timestamp'] = datetime.now().isoformat()
    
    # Store log
    with logs_lock:
        logs.append(data)
    
    # Log to file
    log_level = getattr(logging, data['level'].upper(), logging.INFO)
    logger.log(log_level, f"[{data['service']}] {data['message']}")
    
    return jsonify({'status': 'success'}), 201

@app.route('/logs', methods=['GET'])
def get_logs():
    service = request.args.get('service')
    level = request.args.get('level')
    start_time = request.args.get('start_time')
    end_time = request.args.get('end_time')
    limit = request.args.get('limit', 100, type=int)
    
    with logs_lock:
        filtered_logs = logs.copy()
    
    # Apply filters
    if service:
        filtered_logs = [log for log in filtered_logs if log.get('service') == service]
    
    if level:
        filtered_logs = [log for log in filtered_logs if log.get('level') == level]
    
    if start_time:
        filtered_logs = [log for log in filtered_logs if log.get('timestamp', '') >= start_time]
    
    if end_time:
        filtered_logs = [log for log in filtered_logs if log.get('timestamp', '') <= end_time]
    
    # Sort by timestamp (newest first)
    filtered_logs.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
    
    # Apply limit
    filtered_logs = filtered_logs[:limit]
    
    return jsonify(filtered_logs)

@app.route('/services', methods=['GET'])
def get_services():
    with logs_lock:
        services = list(set(log.get('service') for log in logs if 'service' in log))
    
    return jsonify(services)

@app.route('/levels', methods=['GET'])
def get_levels():
    with logs_lock:
        levels = list(set(log.get('level') for log in logs if 'level' in log))
    
    return jsonify(levels)

@app.route('/stats', methods=['GET'])
def get_stats():
    service = request.args.get('service')
    
    with logs_lock:
        filtered_logs = logs.copy()
    
    if service:
        filtered_logs = [log for log in filtered_logs if log.get('service') == service]
    
    # Count logs by level
    level_counts = {}
    for log in filtered_logs:
        level = log.get('level', 'unknown')
        level_counts[level] = level_counts.get(level, 0) + 1
    
    # Count logs by service
    service_counts = {}
    for log in filtered_logs:
        svc = log.get('service', 'unknown')
        service_counts[svc] = service_counts.get(svc, 0) + 1
    
    return jsonify({
        'total_logs': len(filtered_logs),
        'by_level': level_counts,
        'by_service': service_counts
    })

if __name__ == '__main__':
    # Create logs directory if it doesn't exist
    os.makedirs('logs', exist_ok=True)
    
    port = int(os.getenv('PORT', 5007))
    app.run(host='0.0.0.0', port=port, debug=True)
