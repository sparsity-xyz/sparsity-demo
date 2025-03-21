#!/usr/bin/env python3

import os
import logging
import json
from flask import Flask, request, jsonify
from flask_sock import Sock
from enclave_connector import create_connector

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('simple-parent')

app = Flask(__name__)
sock = Sock(app)

# Create the enclave connector
connector = create_connector()

@app.route('/<path:path>', methods=['GET', 'POST'])
def handle_request(path):
    """Forward all HTTP requests to the enclave"""
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

@sock.route('/ws')
def handle_websocket(ws):
    """Handle WebSocket connections"""
    try:
        logger.info("Client connected")
        # Send initial connection message
        ws.send(json.dumps({"status": "connected", "message": "Connected to parent application"}))
        
        while True:
            # Receive message from client
            message = ws.receive()
            try:
                data = json.loads(message)
                
                # Send request to enclave
                response = connector.send_request(data)
                
                # Send response back to client
                ws.send(json.dumps(response))
            except json.JSONDecodeError:
                ws.send(json.dumps({"error": "Invalid JSON format"}))
            except Exception as e:
                logger.error(f"Error handling request: {e}")
                ws.send(json.dumps({"error": str(e)}))
                
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        logger.info("Client disconnected")

if __name__ == '__main__':
    # Wait for enclave to be ready
    connector.wait_for_enclave()
    
    # Start the Flask app
    app.run(host='0.0.0.0', port=8000, debug=True) 