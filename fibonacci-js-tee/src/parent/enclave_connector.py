#!/usr/bin/env python3

import os
import json
import socket
import struct
import time
import logging
import traceback
import base64
import random
import string
import abc

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('enclave-connector')

def generate_random_nonce(length=16):
    """Generate a random nonce string"""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

class EnclaveConnector(abc.ABC):
    """
    Abstract base class defining the interface for enclave connectors.
    Implementations should handle the specifics of connecting to either
    a simulated enclave or a real Nitro Enclave.
    """
    
    @abc.abstractmethod
    def send_request(self, request_data, timeout=5):
        """
        Send a request to the enclave
        
        Args:
            request_data: Request data to send (dict with endpoint and data)
            timeout: Request timeout in seconds
            
        Returns:
            dict: Response data or None on failure
        """
        pass
    
    @abc.abstractmethod
    def wait_for_enclave(self, max_retries=30, retry_interval=1):
        """
        Wait for the enclave to be ready
        
        Args:
            max_retries: Maximum number of retries
            retry_interval: Time between retries in seconds
            
        Returns:
            bool: True if enclave is ready, False otherwise
        """
        pass
    
    def get_attestation(self):
        """Get attestation from the enclave"""
        logger.info("Getting attestation from enclave...")
        try:
            # Create a request for attestation
            nonce = generate_random_nonce()
            request_data = {
                "endpoint": "/attest",
                "data": {
                    "nonce": nonce
                }
            }
            
            # Send the request to the enclave
            return self.send_request(request_data)
        except Exception as e:
            logger.error(f"Error getting attestation: {e}")
            logger.error(traceback.format_exc())
            return {"error": str(e)}

class SimulationConnector(EnclaveConnector):
    """
    Connector for simulation mode using HTTP
    """
    
    def __init__(self):
        """Initialize the connector with environment variables"""
        # Use container name for network communication
        self.enclave_host = os.environ.get('ENCLAVE_HOST', 'enclave')
        self.enclave_port = int(os.environ.get('ENCLAVE_PORT', '5000'))
        self.base_url = f"http://{self.enclave_host}:{self.enclave_port}"
        logger.info(f"Initialized SimulationConnector with URL={self.base_url}")
        
        # Import requests here to avoid dependency in Nitro mode
        import requests
        self.requests = requests
    
    def send_request(self, request_data, timeout=5):
        """Send a request to the enclave"""
        logger.info(f"Sending request to enclave: {request_data}")
        try:
            endpoint = request_data.get("endpoint", "").lstrip("/")
            data = request_data.get("data", {})
            
            url = f"{self.base_url}/{endpoint}"
            logger.info(f"Sending request to URL: {url}")
            
            response = self.requests.post(url, json=data, timeout=timeout)
            
            if response.status_code != 200:
                logger.error(f"Error response from enclave: {response.status_code} - {response.text}")
                return {"error": f"HTTP error: {response.status_code}"}
            
            response_data = response.json()
            logger.info(f"Received response: {response_data}")
            return response_data
        except Exception as e:
            logger.error(f"Error sending request: {e}")
            logger.error(traceback.format_exc())
            return {"error": str(e)}
    
    def wait_for_enclave(self, max_retries=30, retry_interval=1):
        """Wait for the enclave to be ready"""
        logger.info(f"Waiting for enclave at {self.base_url}...")
        
        retries = 0
        while retries < max_retries:
            try:
                response = self.requests.get(f"{self.base_url}/health", timeout=retry_interval)
                if response.status_code == 200:
                    logger.info(f"Enclave is ready after {retries} seconds")
                    return True
            except Exception:
                pass
            
            retries += 1
            time.sleep(retry_interval)
        
        logger.warning(f"Enclave might not be ready after {max_retries} seconds")
        return False

class NitroConnector(EnclaveConnector):
    """
    Connector for AWS Nitro Enclaves using VSOCK
    """
    
    def __init__(self):
        """Initialize the connector with environment variables"""
        self.enclave_cid = int(os.environ.get('ENCLAVE_CID', '16'))
        self.vsock_port = int(os.environ.get('VSOCK_PORT', '5000'))
        logger.info(f"Initialized NitroConnector with CID={self.enclave_cid}, PORT={self.vsock_port}")
    
    def send_request(self, request_data, timeout=5):
        """Send a request to the enclave using VSOCK"""
        logger.info(f"Sending request to enclave: {request_data}")
        try:
            # Create a VSOCK socket
            sock = socket.socket(socket.AF_VSOCK, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            
            # Connect to the enclave
            logger.info(f"Connecting to enclave CID={self.enclave_cid}, PORT={self.vsock_port}")
            sock.connect((self.enclave_cid, self.vsock_port))
            
            # Convert the request to JSON and encode as bytes
            request_bytes = json.dumps(request_data).encode('utf-8')
            request_len = len(request_bytes)
            
            # Send the request length followed by the request data
            logger.info(f"Sending request length: {request_len}")
            sock.sendall(struct.pack("!I", request_len))
            sock.sendall(request_bytes)
            
            # Receive the response length
            logger.info("Waiting for response length...")
            response_len_bytes = sock.recv(4)
            if not response_len_bytes:
                logger.error("Empty response length received")
                sock.close()
                return {"error": "Empty response from enclave"}
            
            response_len = struct.unpack("!I", response_len_bytes)[0]
            logger.info(f"Response length: {response_len}")
            
            # Receive the response data
            logger.info("Receiving response data...")
            response_bytes = b""
            while len(response_bytes) < response_len:
                chunk = sock.recv(response_len - len(response_bytes))
                if not chunk:
                    break
                response_bytes += chunk
            
            # Parse the response
            response_data = json.loads(response_bytes.decode('utf-8'))
            logger.info(f"Response received: {response_data}")
            
            # Close the socket
            sock.close()
            
            return response_data
        except Exception as e:
            logger.error(f"Error sending request: {e}")
            logger.error(traceback.format_exc())
            return {"error": str(e)}
    
    def wait_for_enclave(self, max_retries=30, retry_interval=1):
        """Wait for the Nitro Enclave to be ready"""
        logger.info("Waiting for Nitro Enclave to start...")
        
        retries = 0
        while retries < max_retries:
            try:
                # Try to connect to the VSOCK port
                sock = socket.socket(socket.AF_VSOCK, socket.SOCK_STREAM)
                sock.settimeout(retry_interval)
                result = sock.connect_ex((self.enclave_cid, self.vsock_port))
                sock.close()
                if result == 0:
                    logger.info(f"Nitro Enclave is ready after {retries} seconds")
                    return True
            except Exception:
                pass
            
            retries += 1
            time.sleep(retry_interval)
        
        logger.warning("Warning: Nitro Enclave might not be ready")
        return False

def create_connector():
    """Create the appropriate connector based on environment"""
    env_setup = os.environ.get('ENV_SETUP', 'SIM').upper()
    
    if env_setup == 'NITRO':
        logger.info("Creating NitroConnector")
        return NitroConnector()
    else:
        logger.info("Creating SimulationConnector")
        return SimulationConnector() 