#!/usr/bin/env python3

import json
import os
import time
import socket
import struct
import threading
import logging
import sys
import traceback
import base64
import uuid
import hashlib
import random
import string

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('enclave-base')

class BaseEnclaveApp:
    """
    Base class for enclave applications that provides common functionality
    for request handling, KMS operations, and communication with the parent instance.
    
    This class delegates specific responsibilities to appropriate services:
    - ParentConnector: Handles communication with the parent instance (HTTP or VSOCK)
    - KmsService: Handles cryptographic operations, attestation, and AWS KMS interactions
    
    This architecture follows a clean separation of concerns:
    - BaseEnclaveApp: Core application logic and request routing
    - ParentConnector: Communication details (protocol-specific)
    - KmsService: Cryptography and KMS operations (environment-specific)
    
    Subclasses can extend this by overriding the get_custom_handler method
    to add support for custom endpoints and application-specific behavior.
    """
    
    def __init__(self, connector=None, kms_service=None):
        """
        Initialize the base enclave application with common settings
        
        Args:
            connector (ParentConnector, optional): Server connector for parent communication.
                If None, a connector will be created based on environment.
            kms_service (KmsService, optional): KMS service for cryptography operations.
                If None, a KMS service will be created based on environment.
        """
        # Print startup information
        logger.info("=== Enclave Application Initializing ===")
        logger.info(f"Python version: {sys.version}")
        logger.info(f"Environment variables: {dict(os.environ)}")

        # VSOCK configuration for communication with parent instance
        self.vsock_port = int(os.environ.get('VSOCK_PORT', 5000))
        self.parent_cid = 3  # Parent CID is always 3 in Nitro Enclaves

        # Generate a unique ID for this enclave instance
        self.enclave_id = str(uuid.uuid4())
        logger.info(f"Generated enclave ID: {self.enclave_id}")

        # Store AWS credentials received from parent instance
        self.aws_credentials = {
            "aws_access_key_id": os.environ.get('AWS_ACCESS_KEY_ID', ''),
            "aws_secret_access_key": os.environ.get('AWS_SECRET_ACCESS_KEY', ''),
            "aws_session_token": os.environ.get('AWS_SESSION_TOKEN', ''),
            "region": "us-east-1",  # Default region
            "kms_key_id": ""
        }

        # Set debug mode based on environment variable
        self.debug_mode = os.environ.get('DEBUG', 'false').lower() in ('true', '1', 'yes')
        
        # Create services if not provided
        if not connector or not kms_service:
            connector, kms_service = self._create_services()
        
        # Set instance variables
        self.connector = connector
        self.kms_service = kms_service
            
        # Set up the request handler in the connector
        if self.connector:
            self.connector.request_handler = self.handle_request
            logger.info("Set up request handler in connector")
            
        # Initialize cryptography components
        self.crypto_available = False
        self.signing_public_key_pem = ""
        self.init_crypto()
    
    def _create_services(self):
        """
        Create the connector and KMS service if not provided.
        
        Returns:
            tuple: (connector, kms_service) - The created services
        """
        try:
            # Create the connector if not provided
            connector = None
            if os.environ.get('ENV_SETUP') == 'SIM':
                from parent_connector import HttpServerConnector
                connector = HttpServerConnector()
                logger.info("Created connector: HttpServerConnector")
            else:
                from parent_connector import VsockServerConnector
                connector = VsockServerConnector()
                logger.info("Created connector: VsockServerConnector")
            
            # Create the KMS service if not provided
            from kms_service import MockKmsService
            kms_service = MockKmsService(self.enclave_id)
            logger.info("Created KMS service: MockKmsService")
            
            return connector, kms_service
        except Exception as e:
            logger.error(f"Error creating services: {e}")
            logger.error(traceback.format_exc())
            return None, None
    
    def init_crypto(self):
        """
        Initialize cryptography components for signing.
        
        This method delegates to the KMS service's init_crypto method,
        which will configure crypto operations appropriately for the environment.
        """
        self.crypto_available = False
        self.signing_public_key_pem = ""
        
        # Use KMS service for all crypto operations if available
        if hasattr(self, 'kms_service') and self.kms_service:
            # Initialize the KMS service's crypto capabilities
            if hasattr(self.kms_service, 'init_crypto'):
                crypto_info = self.kms_service.init_crypto()
                
                # If we got crypto info back, we can use it
                if crypto_info:
                    self.crypto_available = True
                    # Store the public key if provided
                    if 'public_key_pem' in crypto_info:
                        self.signing_public_key_pem = crypto_info['public_key_pem']
                    logger.info("Initialized crypto using KMS service")
                    return
        
        logger.warning("No KMS service available for crypto operations or initialization failed")
    
    def sign_data(self, data):
        """
        Sign data using available cryptographic mechanisms
        
        Args:
            data: Data to sign (bytes or string)
            
        Returns:
            str: Base64-encoded signature
        """
        if not self.crypto_available:
            # Return a placeholder signature if cryptography is not available
            return base64.b64encode(b"crypto_unavailable").decode('utf-8')
        
        # Ensure data is bytes
        if not isinstance(data, bytes):
            data = str(data).encode('utf-8')
        
        # Delegate signing to the KMS service
        if hasattr(self, 'kms_service') and self.kms_service:
            signature = self.kms_service.sign_data(data)
            if signature:
                return signature
        
        # Fall back to placeholder if KMS service isn't available
        logger.warning("No KMS service available for signing, using placeholder")
        return base64.b64encode(b"signing_service_unavailable").decode('utf-8')
    
    def secure_hash(self, data):
        """Create a secure hash of data"""
        if isinstance(data, dict):
            data = json.dumps(data, sort_keys=True)
        if not isinstance(data, bytes):
            data = str(data).encode('utf-8')
        return hashlib.sha256(data).hexdigest()
    
    def generate_random_nonce(self, length=16):
        """Generate a random nonce for attestation"""
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))
    
    def handle_health_request(self, data):
        """Handle a health check request"""
        response = {
            "status": "healthy", 
            "timestamp": int(time.time()),
            "debug_mode": self.debug_mode,
            "enclave_id": self.enclave_id
        }
        # Add signature to response
        signature = self.sign_data(json.dumps(response, sort_keys=True))
        response["signature"] = signature
        return response
    
    def handle_attestation_request(self, data):
        """
        Handle an attestation request
        
        Args:
            data (dict): Request data containing an optional nonce
            
        Returns:
            dict: Response containing attestation document and status
        """
        try:
            # Get nonce from request data or generate one
            nonce = data.get("nonce")
            if not nonce:
                nonce = self.generate_random_nonce()
                logger.info(f"Generated nonce: {nonce}")
            
            # Generate attestation using KMS service
            attestation = self.generate_attestation(nonce)
            if attestation:
                return {
                    "status": "success",
                    "attestation": attestation,
                    "nonce": nonce
                }
            else:
                return {
                    "status": "error",
                    "message": "Failed to generate attestation"
                }, 500
        except Exception as e:
            logger.error(f"Error generating attestation: {e}")
            logger.error(traceback.format_exc())
            return {
                "status": "error",
                "message": str(e)
            }, 500
    
    def generate_attestation(self, nonce=None):
        """
        Generate an attestation document with the provided nonce
        
        Args:
            nonce (str, optional): A nonce to include in the attestation document.
                If not provided, a random nonce will be generated.
                
        Returns:
            dict: The attestation document and related information.
        """
        # Generate a nonce if not provided
        if not nonce:
            nonce = self.generate_random_nonce()
        
        # Delegate attestation generation to the KMS service
        if hasattr(self, 'kms_service') and self.kms_service:
            return self.kms_service.generate_attestation(nonce=nonce)
        
        # If KMS service is not available, return an error
        logger.error("No attestation generation capability available")
        return {"error": "Attestation generation not available", "nonce": nonce}
    
    def handle_kms_request(self, data):
        """Handle a KMS operation request"""
        # Perform a KMS operation
        operation = data.get("operation")
        if not operation:
            return {"error": "Missing operation parameter"}
        
        if operation not in ["decrypt", "genkey", "genrandom"]:
            return {"error": f"Unsupported operation: {operation}"}
        
        # Pass all other parameters to the KMS operation
        kwargs = {k: v for k, v in data.items() if k != "operation"}
        
        return self.perform_kms_operation(operation, **kwargs)
    
    def perform_kms_operation(self, operation, **kwargs):
        """
        Perform a KMS operation using the KMS service
        
        Args:
            operation (str): The KMS operation to perform (decrypt, genkey, genrandom).
            **kwargs: Additional arguments for the operation.
            
        Returns:
            dict: The result of the KMS operation.
        """
        # Use the KMS service to perform the operation
        if self.kms_service:
            # Perform the operation
            if operation == "decrypt":
                return self.kms_service.decrypt(**kwargs)
            elif operation == "genkey":
                return self.kms_service.generate_key(**kwargs)
            elif operation == "genrandom":
                return self.kms_service.generate_random(**kwargs)
        
        # If KMS service is not available, return an error
        logger.error("KMS service not available for performing operations")
        return {"error": "KMS service not available"}
    
    def handle_credentials_request(self, data):
        """
        Handle a request to update AWS credentials
        
        Args:
            data (dict): The new credentials
            
        Returns:
            dict: Success or failure response
        """
        # Update AWS credentials
        success = self.update_aws_credentials(data)
        
        # Return success response
        return {
            "status": "success" if success else "warning",
            "message": "AWS credentials updated successfully" if success else "AWS credentials partially updated",
            "timestamp": int(time.time())
        }
    
    def get_aws_credentials(self):
        """
        Get the current AWS credentials
        
        Returns:
            dict: The current AWS credentials
        """
        return self.aws_credentials
    
    def update_aws_credentials(self, new_credentials):
        """
        Update the AWS credentials both in this class and in the KMS service
        
        Args:
            new_credentials (dict): The new AWS credentials
            
        Returns:
            bool: True if the credentials were updated successfully
        """
        # Update our local copy of credentials
        for key, value in new_credentials.items():
            if key in self.aws_credentials and value is not None:
                self.aws_credentials[key] = value
                
                # Log the update (safely for sensitive fields)
                if key == "aws_access_key_id" and value:
                    masked_key = value[:4] + "..." + value[-4:] if len(value) > 8 else "****"
                    logger.info(f"AWS access key ID updated: {masked_key}")
                elif key == "aws_secret_access_key" and value:
                    logger.info("AWS secret access key updated (value not logged)")
                elif key == "aws_session_token" and value:
                    logger.info("AWS session token updated (value not logged)")
                elif key == "region":
                    logger.info(f"AWS region updated to {value}")
                elif key == "kms_key_id":
                    logger.info(f"KMS key ID updated to {value}")
        
        # Log the credential state (safely)
        logger.info(f"AWS credentials status: Access Key: {'SET' if self.aws_credentials['aws_access_key_id'] else 'NOT SET'}, Secret Key: {'SET' if self.aws_credentials['aws_secret_access_key'] else 'NOT SET'}, Session Token: {'SET' if self.aws_credentials['aws_session_token'] else 'NOT SET'}, Region: {self.aws_credentials['region']}")
        
        # Update the credentials in the KMS service
        if self.kms_service:
            try:
                self.kms_service.update_credentials(self.aws_credentials)
                logger.info("KMS service credentials updated successfully")
                return True
            except Exception as e:
                logger.warning(f"Failed to update KMS service credentials: {e}")
                return False
        
        return True
    
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
            
            # Handle standard endpoints
            if endpoint == "/health":
                return self.handle_health_request(data)
            elif endpoint == "/attest":
                return self.handle_attestation_request(data)
            elif endpoint == "/set-credentials":
                return self.handle_credentials_request(data)
            
            # For any other endpoint, return a simple response
            return {
                "status": "success",
                "message": f"Base enclave received request at {endpoint}",
                "data": data
            }
            
        except Exception as e:
            logger.error(f"Error handling request: {e}")
            logger.error(traceback.format_exc())
            return {"error": str(e)}, 500
    
    def get_custom_handler(self, request_data):
        """
        Get a custom handler for the given endpoint
        
        This method should be overridden by derived classes to handle application-specific
        endpoints. The base implementation returns None for all endpoints.
        
        Example implementation in a derived class:
        ```python
        def get_custom_handler(self, request_data):
            if request_data.get("endpoint") == "/my-custom-endpoint":
                return self.handle_my_custom_endpoint
            return super().get_custom_handler(request_data)  # Fall back to base handlers
        ```
        
        Args:
            request_data (dict or str): The request data containing endpoint and data,
                or a string containing the endpoint
            
        Returns:
            callable: A function that takes a data dictionary and returns a response,
                or None if no handler is available for the endpoint
        """
        return None
    
    def run(self):
        """
        Run the enclave application.
        This method starts the connector and begins handling requests.
        """
        try:
            logger.info("Enclave application starting...")
            
            # Start the connector
            if self.connector:
                self.connector.run()
            else:
                logger.error("No connector available")
                return
            
            # Keep the main thread alive
            while True:
                time.sleep(1)
        except Exception as e:
            logger.error(f"Main function error: {e}")
            logger.error(traceback.format_exc())
            logger.info("Sleeping for 60 seconds before exiting...")
            time.sleep(60)
    
    def start(self):
        """
        Start the enclave application (deprecated, use run() instead)
        
        This method is kept for backward compatibility and simply calls run()
        """
        logger.warning("The start() method is deprecated. Please use run() instead.")
        return self.run() 