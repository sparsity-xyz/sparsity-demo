#!/usr/bin/env python3

import json
import time
import logging
import random
import string
import traceback
from base_enclave_app import BaseEnclaveApp
import sys
import base64

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('simple-enclave')

class SimpleEnclaveApp(BaseEnclaveApp):
    """
    Simple enclave application that extends the BaseEnclaveApp with
    a custom Fibonacci calculation endpoint.
    """
    
    def __init__(self, env_setup=None):
        """
        Initialize the simple enclave application
        
        Args:
            env_setup (str, optional): Environment setup string ('NITRO' or 'SIM').
                If None, will use ENV_SETUP environment variable.
        """
        super().__init__(env_setup=env_setup)
        logger.info("SimpleEnclaveApp initialized")
        # Remove initial calculation since we'll now wait for initialization data
        self.result = None

    def initialize(self, raw_bytes):
        """
        Override the base initialize method to handle Fibonacci calculation
        from initialization data.
        
        Args:
            raw_bytes (bytes): The raw bytes containing the Fibonacci input number
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not isinstance(raw_bytes, bytes):
                logger.error("Input must be raw bytes")
                return False

            # Store the initialization data
            self.init_data = raw_bytes
                
            # Convert bytes to integer (big-endian)
            n = int.from_bytes(raw_bytes, byteorder='big')
            logger.info(f"Initializing with Fibonacci calculation for n={n}")
                
            # Calculate Fibonacci number
            result = self.calculate_fibonacci(n)
                
            # Store result as bytes
            self.result = result.to_bytes(32, 'big')
            
            logger.info(f"Successfully calculated Fibonacci({n}) = {result}")
            return True
            
        except Exception as e:
            logger.error(f"Error in initialize: {e}")
            logger.error(traceback.format_exc())
            return False

    def calculate_fibonacci(self, n):
        """
        Calculate the nth Fibonacci number
        
        Args:
            n (int): The index of the Fibonacci number to calculate
            
        Returns:
            int: The nth Fibonacci number
        """
        if n <= 0:
            return 0
        elif n == 1:
            return 1
        
        a, b = 0, 1
        for _ in range(2, n + 1):
            a, b = b, a + b
        
        return b
    
    def handle_request(self, request_data):
        """
        Handle incoming requests by routing them to appropriate handlers
        
        Args:
            request_data (dict or str): Request data containing endpoint and data, or just the endpoint string
            
        Returns:
            dict: Response data
        """
        try:
            # Parse request data
            if isinstance(request_data, str):
                endpoint = request_data
                data = {}
            else:
                endpoint = request_data.get("endpoint", "")
                data = request_data.get("data", {})
            
            # Handle settlement request - this is what the contract uses for verification
            if endpoint == "/settlement":
                # Check if we have a result
                if self.result is None:
                    return {
                        "status": "running",
                        "computation_status": "running",
                        "timestamp": int(time.time()),
                        "debug_mode": False,
                        "enclave_id": self.enclave_id,
                        "result": "",
                        "signature": ""
                    }
                
                # The contract expects to verify raw bytes (self.result), not the JSON
                # We should sign exactly what the contract expects to verify
                raw_bytes_to_sign = self.result  # This is what the contract expects
                
                # Sign the raw bytes
                signature = self.sign_data(raw_bytes_to_sign)
                
                # Create the response
                response = {
                    "status": "success",
                    "computation_status": "completed",
                    "timestamp": int(time.time()),
                    "debug_mode": False,
                    "enclave_id": self.enclave_id,
                    "result": base64.b64encode(self.result).decode('utf-8'),
                    "signature": base64.b64encode(signature).decode('utf-8')
                }
                
                return response
            
            # Handle Fibonacci calculation request
            elif endpoint.startswith("/fibonacci/"):
                # Extract number from URL path
                try:
                    n = int(endpoint.split("/")[-1])
                except (ValueError, IndexError):
                    return {"error": "Invalid number in URL"}, 400
                
                if n < 0:
                    return {"error": "Input must be non-negative"}, 400
                
                # Calculate Fibonacci number
                result = self.calculate_fibonacci(n)
                
                # Convert result to bytes and store it for later use
                self.result = result.to_bytes(32, 'big')
                
                # Create response for the client
                response = {
                    "status": "success",
                    "enclave_id": self.enclave_id,
                    "input": n,
                    "result": result,
                    "timestamp": int(time.time())
                }
                
                return response
            
            # Let the base class handle standard endpoints
            return super().handle_request(request_data)
            
        except Exception as e:
            logger.error(f"Error handling request: {e}")
            logger.error(traceback.format_exc())
            return {
                "status": "error",
                "message": str(e)
            }

if __name__ == '__main__':
    # Get environment setup from command line argument
    env_setup = sys.argv[1] if len(sys.argv) > 1 else None
    
    # Create and start the simple enclave application
    app = SimpleEnclaveApp(env_setup=env_setup)
    app.run()