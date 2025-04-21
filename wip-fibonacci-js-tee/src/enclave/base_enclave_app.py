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

from kms_service import create_kms_service
from parent_connector import create_server_connector

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
    
    def __init__(self, env_setup=None):
        """
        Initialize the base enclave application with common settings
        
        Args:
            env_setup (str, optional): Environment setup string ('NITRO' or 'SIM').
                If None, will use ENV_SETUP environment variable.
        """
        # Print startup information
        logger.info("=== Enclave Application Initializing ===")
        logger.info(f"Python version: {sys.version}")
        logger.info(f"Environment variables: {dict(os.environ)}")

        # Store environment setup
        self.env_setup = env_setup or os.environ.get('ENV_SETUP', 'NITRO')
        logger.info(f"Using environment setup: {self.env_setup}")

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
        
        # Create services based on environment
        self.connector, self.kms_service = self._create_services()
        
        # Set up the request handler in the connector
        if self.connector:
            self.connector.request_handler = self.handle_request
            logger.info("Set up request handler in connector")
            
        # Initialize cryptography components
        self.crypto_available = False
        self.signing_public_key_pem = ""
        self.result = None  # Initialize result as None
        self.init_data = None  # Initialize init_data as None
        self.init_crypto()
    
    def _create_services(self):
        """
        Create the connector and KMS service based on the environment setup.
        
        Returns:
            tuple: (connector, kms_service) - The created services
        """
        try:
            # Create the connector
            connector = create_server_connector(self.env_setup)
            
            # Create the KMS service
            kms_service = create_kms_service(self.env_setup)
            
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
    
    def sign_data(self, data) -> bytes:
        """
        Sign data using available cryptographic mechanisms
        
        Args:
            data: Data to sign (bytes or string)
            
        Returns:
            str: Base64-encoded signature
        """
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
        return b"signing_service_unavailable"
    
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
    
    def handle_status_request(self, data):
        """Handle a status request"""
        status = "completed" if self.result is not None else "running"
        
        response = {
            "status": "success",
            "computation_status": status,
            "timestamp": int(time.time()),
            "debug_mode": self.debug_mode,
            "enclave_id": self.enclave_id
        }
        
        # Include result if available
        response["result"] = base64.b64encode(self.result).decode('utf-8') if self.result else ""
        response["signature"] = base64.b64encode(self.sign_data(json.dumps(response, sort_keys=True))).decode('utf-8')
            
        return response
    
    def handle_attestation_request(self, data):
        """
        Handle a request for attestation document
        
        Args:
            data (dict): Request data containing an optional nonce
            
        Returns:
            dict: Response containing the attestation document
        """
        try:
            logger.info("Received attestation request")
            
            # Access the NSM utility directly through the KMS service
            if not hasattr(self, 'kms_service') or not self.kms_service:
                return {
                    "status": "error",
                    "message": "KMS service not available"
                }, 500
            
            # Get attestation document from NSM
            attestation_doc = self.kms_service.generate_attestation()
            if not attestation_doc:
                return {
                    "status": "error",
                    "message": "Failed to get attestation document from NSM"
                }, 500
            
            # Convert to base64 for transmission
            attestation_doc_b64 = base64.b64encode(attestation_doc).decode('utf-8')
            
            response = {
                "status": "success",
                "attestation": {
                    "attestation_doc": attestation_doc_b64,
                    "timestamp": int(time.time()),
                    "enclave_id": self.enclave_id
                }
            }
            
            return response
            
        except Exception as e:
            logger.error(f"Error getting attestation document: {e}")
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
    
    def handle_formatted_attestation_request(self, data):
        """
        Handle a request for a formatted, human-readable attestation document
        
        Args:
            data (dict): Request data containing an optional nonce
            
        Returns:
            dict: Response containing the parsed and formatted attestation document
        """
        try:
            logger.info("Received request for formatted attestation document")
            
            # Access the NSM utility directly through the KMS service
            if not hasattr(self, 'kms_service') or not self.kms_service:
                return {
                    "status": "error",
                    "message": "KMS service not available"
                }, 500
            
            # Get attestation document from NSM
            attestation_doc = self.kms_service.generate_attestation()
            if not attestation_doc:
                return {
                    "status": "error",
                    "message": "Failed to get attestation document from NSM"
                }, 500
            
            try:
                # Import cbor2 library for parsing attestation document
                import cbor2
                import json
                
                # Parse and format the attestation document
                def parse_attestation_doc(attestation_doc):
                    # Decode CBOR attestation document
                    data = cbor2.loads(attestation_doc)
                    
                    # Load and decode document payload (position 2 contains the document)
                    doc = data[2]
                    doc_obj = cbor2.loads(doc)
                    
                    # Format the document for readability
                    formatted_doc = {
                        # PCR measurements with descriptive comments
                        "pcrs": {
                            str(idx): {
                                "value": val.hex() if isinstance(val, bytes) else val,
                                "description": {
                                    "0": "BIOS/firmware measurement",
                                    "1": "Platform configuration",
                                    "2": "Kernel and boot modules",
                                    "4": "Application code and data"
                                }.get(str(idx), "Unused PCR")
                            }
                            for idx, val in doc_obj.get('pcrs', {}).items()
                        },
                        
                        # Certificate information
                        "certificate": base64.b64encode(doc_obj.get('certificate', b'')).decode('utf-8') if isinstance(doc_obj.get('certificate', b''), bytes) else None,
                        "cabundle": [cert.hex() for cert in doc_obj.get('cabundle', [])] if 'cabundle' in doc_obj else None,
                        
                        # Public key for verification
                        "public_key": base64.b64encode(doc_obj.get('public_key', b'')).decode('utf-8') if isinstance(doc_obj.get('public_key', b''), bytes) else None,
                        
                        # Timestamp and metadata
                        "timestamp": doc_obj.get('timestamp', 0),
                        "timestamp_formatted": time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime(doc_obj.get('timestamp', 0)/1000)),
                        
                        # Optional fields
                        "nonce": doc_obj.get('nonce', b'').decode('utf-8') if isinstance(doc_obj.get('nonce', b''), bytes) else None,
                        "user_data": doc_obj.get('user_data', b'').decode('utf-8') if isinstance(doc_obj.get('user_data', b''), bytes) else None
                    }
                    
                    return formatted_doc
                
                # Get formatted document
                formatted_doc = parse_attestation_doc(attestation_doc)
                
                # Log successful parsing
                active_pcrs = [idx for idx, data in formatted_doc['pcrs'].items() 
                             if data['value'] != "0"*96]  # 96 is the length of a zero PCR value
                logger.info(f"Successfully parsed attestation document. Active PCRs: {active_pcrs}")
                
                return {
                    "status": "success",
                    "attestation": formatted_doc
                }
                
            except ImportError:
                logger.warning("cbor2 library not available, cannot parse attestation document")
                return {
                    "status": "error",
                    "message": "cbor2 library not available for parsing"
                }, 500
            except Exception as parse_error:
                logger.error(f"Failed to parse attestation document: {parse_error}")
                logger.error(traceback.format_exc())
                return {
                    "status": "error",
                    "message": f"Failed to parse attestation document: {str(parse_error)}"
                }, 500
            
        except Exception as e:
            logger.error(f"Error getting attestation document: {e}")
            logger.error(traceback.format_exc())
            return {
                "status": "error",
                "message": str(e)
            }, 500
    
    def initialize(self, raw_bytes):
        """
        Default initialize method that stores the raw bytes data.
        Subclasses can override this to provide custom initialization logic.
        
        Args:
            raw_bytes (bytes): The raw bytes to initialize with
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not isinstance(raw_bytes, bytes):
                logger.error("Input must be raw bytes")
                return False
                
            self.init_data = raw_bytes
            logger.info("Successfully stored initialization data")
            return True
            
        except Exception as e:
            logger.error(f"Error storing initialization data: {e}")
            logger.error(traceback.format_exc())
            return False

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
            # Handle settlement too for now
            if endpoint == "/status" or endpoint == "/settlement":
                return self.handle_status_request(data)
            elif endpoint == "/attest":
                return self.handle_attestation_request(data)
            elif endpoint == "/formatted-attest":
                return self.handle_formatted_attestation_request(data)
            elif endpoint == "/initialize":
                return self.handle_initialize_request(data)
            
            # For any other endpoint, return a simple response
            response = {
                "status": "success",
                "message": f"Base enclave received request at {endpoint}",
                "data": data
            }
            return response
            
        except Exception as e:
            logger.error(f"Error handling request: {e}")
            logger.error(traceback.format_exc())
            return {"error": str(e)}, 500

    def handle_initialize_request(self, data):
        """
        Handle an initialization request with raw bytes data
        
        Args:
            data (dict): Request data containing raw bytes in base64 format
            
        Returns:
            dict: Response indicating success or failure
        """
        try:
            if not isinstance(data, dict) or "data" not in data:
                return {
                    "status": "error",
                    "message": "Request must include 'data' field with base64-encoded bytes"
                }, 400

            # Decode base64 data
            try:
                raw_bytes = base64.b64decode(data["data"])
            except Exception as e:
                return {
                    "status": "error",
                    "message": f"Failed to decode base64 data: {str(e)}"
                }, 400

            # Call initialize method
            if self.initialize(raw_bytes):
                return {
                    "status": "success",
                    "message": "Successfully initialized with provided data"
                }
            else:
                return {
                    "status": "error",
                    "message": "Failed to initialize with provided data"
                }, 500

        except Exception as e:
            logger.error(f"Error handling initialize request: {e}")
            logger.error(traceback.format_exc())
            return {
                "status": "error",
                "message": str(e)
            }, 500
    
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

    def finalize(self, raw_bytes):
        """
        Set the enclave result to the base64-encoded version of the provided raw bytes.
        
        Args:
            raw_bytes (bytes): The raw bytes to be encoded and stored as the result
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not isinstance(raw_bytes, bytes):
                logger.error("Input must be raw bytes")
                return False
                
            self.result = base64.b64encode(raw_bytes).decode('utf-8')
            logger.info("Successfully set enclave result")
            return True
            
        except Exception as e:
            logger.error(f"Error setting enclave result: {e}")
            logger.error(traceback.format_exc())
            return False