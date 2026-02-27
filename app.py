"""
Flask Web Application - Manual trigger for News Auto Collector
"""

import logging
import json
import threading
from datetime import datetime
from flask import Flask, render_template, jsonify, request
from src.main import NewsAutoCollector

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Flask app setup
app = Flask(__name__, static_folder='static', template_folder='templates')

# Global state for tracking execution
execution_state = {
    'running': False,
    'status': 'idle',
    'progress': 0,
    'message': '',
    'doc_url': None,
    'error': None,
    'start_time': None,
    'end_time': None
}


def run_collector():
    """Execute the news collector in a separate thread"""
    global execution_state
    try:
        execution_state['running'] = True
        execution_state['status'] = 'initializing'
        execution_state['progress'] = 0
        execution_state['message'] = 'Initializing...'
        execution_state['error'] = None
        execution_state['start_time'] = datetime.now().isoformat()
        execution_state['end_time'] = None
        
        logger.info("Starting News Auto Collector execution...")
        
        collector = NewsAutoCollector()
        
        execution_state['status'] = 'fetching_data'
        execution_state['progress'] = 15
        execution_state['message'] = 'Fetching keywords and websites...'
        
        execution_state['status'] = 'searching'
        execution_state['progress'] = 30
        execution_state['message'] = 'Searching for articles...'
        
        execution_state['status'] = 'deduplicating'
        execution_state['progress'] = 60
        execution_state['message'] = 'Removing duplicates...'
        
        execution_state['status'] = 'exporting'
        execution_state['progress'] = 85
        execution_state['message'] = 'Exporting to Google Docs...'
        
        # Run the actual collector
        doc_url = collector.run()
        
        execution_state['status'] = 'complete'
        execution_state['progress'] = 100
        execution_state['message'] = 'Completed successfully!'
        execution_state['doc_url'] = doc_url
        execution_state['end_time'] = datetime.now().isoformat()
        
        logger.info(f"Execution completed successfully. Document: {doc_url}")
        
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Execution failed: {error_msg}", exc_info=True)
        execution_state['status'] = 'error'
        execution_state['progress'] = 0
        execution_state['message'] = 'An error occurred during execution'
        execution_state['error'] = error_msg
        execution_state['end_time'] = datetime.now().isoformat()
    
    finally:
        execution_state['running'] = False


@app.route('/')
def index():
    """Render main page"""
    return render_template('index.html')


@app.route('/api/status', methods=['GET'])
def get_status():
    """Get current execution status"""
    return jsonify(execution_state)


@app.route('/api/run', methods=['POST'])
def run_collection():
    """Start news collection"""
    if execution_state['running']:
        return jsonify({
            'success': False,
            'message': 'Execution already in progress'
        }), 409
    
    logger.info("Received request to start collection")
    
    # Start execution in a separate thread
    thread = threading.Thread(target=run_collector, daemon=True)
    thread.start()
    
    return jsonify({
        'success': True,
        'message': 'Execution started'
    })


@app.route('/api/reset', methods=['POST'])
def reset_status():
    """Reset execution status"""
    global execution_state
    if execution_state['running']:
        return jsonify({
            'success': False,
            'message': 'Cannot reset while execution is running'
        }), 409

    execution_state = {
        'running': False,
        'status': 'idle',
        'progress': 0,
        'message': '',
        'doc_url': None,
        'error': None,
        'start_time': None,
        'end_time': None
    }
    
    return jsonify({'success': True, 'message': 'Status reset'})


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({'error': 'Not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {str(error)}", exc_info=True)
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    logger.info("Starting News Auto Collector Web Application")
    logger.info("Open browser at http://localhost:5000")
    app.run(debug=True, port=5000, threaded=True)
