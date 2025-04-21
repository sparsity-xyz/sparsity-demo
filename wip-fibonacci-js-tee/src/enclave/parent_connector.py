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
        self.port = int(os.environ.get('ENCLAVE_PORT', '5000'))
        logger.info(f"Initialized HttpServerConnector with port {self.port}")
    
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
    
    def run(self, host='0.0.0.0', port=None):
        """
        Start the Flask application
        
        Args:
            host (str): Host to bind to
            port (int): Port to listen on, defaults to ENCLAVE_PORT
        """
        # Call parent's run method
        super().run()
        
        # Use configured port if none provided
        if port is None:
            port = self.port
        
        # Start the Flask server
        logger.info(f"Starting Flask server on {host}:{port}")
        self.app.run(host=host, port=port, debug=False)

class VsockServerConnector(ParentConnector):
    """Connector for AWS Nitro Enclaves using VSOCK"""
    
    def __init__(self, port=5000):
        """
        Initialize the VSOCK connector
        
        Args:
            port: VSOCK port to listen on
        """
        super().__init__()
        self.port = port
        self.socket = None
        self.listener_thread = None
        logger.info(f"Initialized VsockServerConnector on port {port}")
    
    def _start_listener(self):
        """Start the VSOCK listener thread"""
        self.listener_thread = threading.Thread(target=self._listen_for_connections)
        self.listener_thread.daemon = True
        self.listener_thread.start()
        logger.info("Started VSOCK listener thread")
    
    def _listen_for_connections(self):
        """Listen for incoming VSOCK connections"""
        try:
            # Create a VSOCK socket
            self.socket = socket.socket(socket.AF_VSOCK, socket.SOCK_STREAM)
            self.socket.bind((socket.VMADDR_CID_ANY, self.port))
            self.socket.listen(5)
            
            logger.info(f"Listening for VSOCK connections on port {self.port}")
            
            while self.running:
                try:
                    # Accept a connection
                    client_socket, addr = self.socket.accept()
                    logger.info(f"Accepted VSOCK connection from CID={addr[0]}, port={addr[1]}")
                    
                    # Handle the connection in a new thread
                    client_thread = threading.Thread(
                        target=self._handle_client,
                        args=(client_socket, addr)
                    )
                    client_thread.daemon = True
                    client_thread.start()
                except Exception as e:
                    if self.running:  # Only log if we're still supposed to be running
                        logger.error(f"Error accepting connection: {e}")
        except Exception as e:
            logger.error(f"Error in VSOCK listener: {e}")
            logger.error(traceback.format_exc())
        finally:
            if self.socket:
                self.socket.close()
            logger.info("VSOCK listener stopped")
    
    def _handle_client(self, client_socket, addr):
        """Handle a client connection"""
        try:
            # Set a timeout for receiving data
            client_socket.settimeout(5)
            
            # Receive the message length
            len_bytes = client_socket.recv(4)
            if not len_bytes:
                logger.warning("Received empty message length")
                return
            
            msg_len = struct.unpack("!I", len_bytes)[0]
            logger.info(f"Receiving message of length {msg_len}")
            
            # Receive the message data
            data_bytes = b""
            while len(data_bytes) < msg_len:
                chunk = client_socket.recv(min(1024, msg_len - len(data_bytes)))
                if not chunk:
                    break
                data_bytes += chunk
            
            # Parse the message
            request_data = json.loads(data_bytes.decode('utf-8'))
            logger.info(f"Received request: {request_data}")
            
            # Handle the request
            if self.request_handler:
                response = self.request_handler(request_data)
                logger.info(f"Generated response: {response}")
                
                # Convert response to JSON and encode as bytes
                response_bytes = json.dumps(response).encode('utf-8')
                response_len = len(response_bytes)
                
                # Send the response length followed by the response data
                client_socket.sendall(struct.pack("!I", response_len))
                client_socket.sendall(response_bytes)
                
                logger.info(f"Sent response of length {response_len}")
            else:
                logger.error("No request handler registered")
        except Exception as e:
            logger.error(f"Error handling client: {e}")
            logger.error(traceback.format_exc())
        finally:
            client_socket.close()
            logger.info("Closed client connection")
    
    def run(self):
        """Run the VSOCK server"""
        super().run()
        logger.info(f"VSOCK server running on port {self.port}")
        
        # Keep the main thread alive
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Received keyboard interrupt, shutting down")
        finally:
            self.stop()

def create_server_connector(env_setup=None):
    """
    Create the appropriate server connector based on environment
    
    Args:
        env_setup (str, optional): Environment setup string ('NITRO' or 'SIM').
            If None, will use ENV_SETUP environment variable.
    """
    if env_setup is None:
        env_setup = os.environ.get('ENV_SETUP', 'SIM').upper()
    
    if env_setup == 'NITRO':
        logger.info("Creating VsockServerConnector")
        return VsockServerConnector(port=int(os.environ.get('VSOCK_PORT', 5000)))
    else:
        logger.info("Creating HttpServerConnector")
        return HttpServerConnector() 