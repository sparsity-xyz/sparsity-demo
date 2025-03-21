#!/usr/bin/env python3

import os
import json
import socket
import struct
import time
import logging
import traceback
import abc
import threading

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('enclave-connector')

class ParentConnector(abc.ABC):
    """
    Abstract base class defining the interface for enclave server connectors.
    Implementations handle the specifics of connecting in different environments.
    """
    
    def __init__(self):
        """Initialize the connector with common attributes"""
        self.running = False
        self.request_handler = None
    
    def run(self, **kwargs):
        """
        Run the connector to listen for incoming connections
        
        Args:
            **kwargs: Additional arguments specific to the connector implementation
        """
        if self.running:
            logger.warning("Connector is already running")
            return
        
        if not self.request_handler:
            logger.error("No request handler registered")
            return
            
        self.running = True
        self._start_listener()
    
    def stop(self):
        """Stop the connector"""
        logger.info("Stopping enclave connector")
        self.running = False
    
    @abc.abstractmethod
    def _start_listener(self):
        """Start listening for connections - to be implemented by subclasses"""
        pass

class HttpServerConnector(ParentConnector):
    """Connector for simulation mode using Flask HTTP server"""
    
    def __init__(self, app=None):
        """
        Initialize the HTTP connector
        
        Args:
            app: Flask application instance, if None, a new instance will be created
        """
        super().__init__()
        
        # Import Flask here to avoid dependency in Nitro mode
        from flask import Flask, request, jsonify
        self.flask = Flask
        self.request = request
        self.jsonify = jsonify
        
        # Store or create Flask app
        self.app = app if app else Flask(__name__)
        logger.info("Initialized HttpServerConnector")
    
    def _start_listener(self):
        """Register routes with Flask"""
        # Register a single catch-all route for all endpoints
        @self.app.route('/<path:endpoint>', methods=['GET', 'POST'])
        def handle_request(endpoint):
            # Format request data for the handler
            request_data = {
                "endpoint": f"/{endpoint}",
                "data": self.request.json if self.request.is_json else {}
            }
            
            # Call the handler and get response
            if self.request_handler:
                response = self.request_handler(request_data)
                return self.jsonify(response)
            else:
                return self.jsonify({"error": "No request handler registered"}), 500
        
        logger.info("Registered HTTP routes with Flask")
    
    def run(self, host='0.0.0.0', port=8000):
        """
        Start the Flask application
        
        Args:
            host (str): Host to bind to
            port (int): Port to listen on
        """
        # Call parent's run method
        super().run()
        
        # Start the Flask server
        logger.info(f"Starting Flask server on {host}:{port}")
        self.app.run(host=host, port=port, debug=False)


def create_server_connector(env_setup: str = None):
    """
    Create the appropriate server connector based on environment
    
    Args:
        env_setup (str, optional): Environment setup ('SIM' or 'NITRO'). 
                                 If None, reads from ENV_SETUP environment variable.
    
    Returns:
        BaseServerConnector: The appropriate server connector instance
    """
    if env_setup is None:
        env_setup = os.environ.get('ENV_SETUP', 'SIM').upper()
    
    if env_setup == 'NITRO':
        logger.info("Creating VsockServerConnector")
        return VsockServerConnector(port=int(os.environ.get('VSOCK_PORT', 5000)))
    else:
        logger.info("Creating HttpServerConnector")
        return HttpServerConnector() 