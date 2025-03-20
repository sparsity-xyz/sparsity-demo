#!/usr/bin/env python3

import os
import logging
from flask import Flask, request, jsonify
from enclave_connector import create_connector

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('simple-parent')

app = Flask(__name__)

# Create the enclave connector
connector = create_connector()

@app.route('/<path:path>', methods=['GET', 'POST'])
def handle_request(path):
    """Forward all requests to the enclave"""
    try:
        # Get request data
        data = request.get_json() if request.is_json else request.args.to_dict()
        
        # Send request to enclave
        response = connector.send_request({
            "endpoint": f"/{path}",
            "data": data
        })
        
        # Return the enclave's response directly
        return jsonify(response)
    except Exception as e:
        logger.error(f"Error forwarding request: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Wait for enclave to be ready
    connector.wait_for_enclave()
    
    # Start the Flask app
    app.run(host='0.0.0.0', port=8000) 