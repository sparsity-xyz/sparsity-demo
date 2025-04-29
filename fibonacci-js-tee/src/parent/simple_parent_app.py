#!/usr/bin/env python3

import os
import base64
import logging
import traceback
from flask import Flask, request, jsonify
from enclave_connector import create_connector

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('simple-parent')

app = Flask(__name__)

initialized = False

# Create the enclave connector
connector = create_connector()

@app.route('/<path:path>', methods=['GET', 'POST'])
def handle_request(path):
    # TODO: make this only run once during app initialization
    global initialized
    if not initialized:
        logger.info("Initializing enclave")
        initialize_enclave()
        initialized = True
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

def initialize_enclave():
    """Initialize the enclave with data from environment variables"""
    try:
        # Get initialization data from environment variable
        init_data = os.environ.get('INIT_DATA')
        if not init_data:
            logger.warning("No initialization data found in environment")
            return
            
        logger.info(f"Found initialization data: {init_data}")
            
        if init_data.startswith('0x'):
            # Remove '0x' prefix if present
            init_data = init_data[2:]
            
        # Convert hex string to bytes and then to base64
        init_bytes = bytes.fromhex(init_data)
        init_base64 = base64.b64encode(init_bytes).decode('utf-8')
        
        logger.info("Sending initialization data to enclave...")
        
        # Send initialization request to enclave
        response = connector.send_request({
            "endpoint": "/initialize",
            "data": {
                "data": init_base64
            }
        })
        
        if response.get("status") == "success":
            logger.info("Successfully initialized enclave")
        else:
            logger.error("Failed to initialize enclave", extra={"response": response})
            
    except Exception as e:
        logger.error(f"Error initializing enclave: {e}")
        logger.error(traceback.format_exc())

if __name__ == '__main__':
    # Wait for enclave to be ready
    connector.wait_for_enclave()

    # Initialize enclave with data from environment
    initialize_enclave()
    
    # Get port from environment variable
    port = int(os.environ.get('PARENT_PORT', 8001))
    
    # Start the Flask app
    logger.info(f"Starting parent application on port {port}")
    app.run(host='0.0.0.0', port=port) 