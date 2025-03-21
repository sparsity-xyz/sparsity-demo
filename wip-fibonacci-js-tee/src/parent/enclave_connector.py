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
        self.enclave_host = os.environ.get('ENCLAVE_HOST', 'enclave')
        self.enclave_port = int(os.environ.get('ENCLAVE_PORT', '8000'))
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

def create_connector(env_setup: str = None):
    """
    Create the appropriate connector based on environment
    
    Args:
        env_setup (str, optional): Environment setup ('SIM' or 'NITRO'). 
                                 If None, reads from ENV_SETUP environment variable.
    
    Returns:
        BaseEnclaveConnector: The appropriate connector instance
    """
    if env_setup is None:
        env_setup = os.environ.get('ENV_SETUP', 'SIM').upper()
    
    logger.info(f"Creating SimulationConnector for {env_setup} environment")
    return SimulationConnector()