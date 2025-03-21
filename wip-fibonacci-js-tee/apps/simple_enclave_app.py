#!/usr/bin/env python3

import json
import time
import logging
import random
import string
import traceback
from base_enclave_app import BaseEnclaveApp

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('simple-enclave')

class SimpleEnclaveApp(BaseEnclaveApp):
    """
    Simple enclave application that extends the BaseEnclaveApp with
    a custom Fibonacci calculation endpoint.
    """
    
    def __init__(self, connector=None, kms_service=None):
        """
        Initialize the simple enclave application
        
        Args:
            connector (EnclaveServerConnector, optional): Server connector for parent communication
            kms_service (KmsService, optional): KMS service for cryptography operations
        """
        super().__init__(connector, kms_service)
        logger.info("SimpleEnclaveApp initialized")
    
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
            # Get endpoint from request data
            endpoint = request_data if isinstance(request_data, str) else request_data.get("endpoint", "")
            
            # Handle Fibonacci calculation request
            if endpoint.startswith("/fibonacci/"):
                # Extract number from URL path
                try:
                    n = int(endpoint.split("/")[-1])
                except (ValueError, IndexError):
                    return {"error": "Invalid number in URL"}, 400
                
                if n < 0:
                    return {"error": "Input must be non-negative"}, 400
                
                # Calculate Fibonacci number
                result = self.calculate_fibonacci(n)
                
                # Create response with signature
                response = {
                    "enclave_id": self.enclave_id,
                    "input": n,
                    "result": result,
                    "timestamp": int(time.time())
                }
                
                # Sign the response
                signature = self.sign_data(json.dumps(response, sort_keys=True))
                response["signature"] = signature
                
                return response
            
            # Let the base class handle standard endpoints
            return super().handle_request(request_data)
            
        except Exception as e:
            logger.error(f"Error handling request: {e}")
            logger.error(traceback.format_exc())
            return {"error": str(e)}, 500

if __name__ == '__main__':
    # Create and start the simple enclave application
    app = SimpleEnclaveApp()
    app.run() 