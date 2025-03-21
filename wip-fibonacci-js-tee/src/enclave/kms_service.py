#!/usr/bin/env python3

import os
import json
import time
import tempfile
import base64
import logging
import traceback
import subprocess
import uuid
import random
import string
import re
import abc
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('kms-service')

class KmsService(abc.ABC):
    """
    Abstract base class for KMS service implementations.
    This class defines the interface that all KMS service implementations must follow.
    """
    
    @abc.abstractmethod
    def init_crypto(self):
        """Initialize cryptographic components"""
        pass
    
    @abc.abstractmethod
    def update_credentials(self, credentials):
        """Update AWS credentials"""
        pass
    
    @abc.abstractmethod
    def decrypt_data(self, encrypted_data, key_id=None, region=None, credentials=None):
        """Decrypt data using KMS"""
        pass
    
    @abc.abstractmethod
    def generate_key(self, key_id=None, key_spec="SYMMETRIC_DEFAULT", region=None, credentials=None):
        """Generate a new key using KMS"""
        pass
    
    @abc.abstractmethod
    def generate_random(self, length=32, region=None, credentials=None):
        """Generate random bytes using KMS"""
        pass
    
    @abc.abstractmethod
    def generate_attestation(self, nonce=None, region=None, credentials=None):
        """Generate an attestation document"""
        pass
    
    @abc.abstractmethod
    def sign_data(self, data, region=None, credentials=None):
        """Sign data using KMS"""
        pass
    
    def extract_attestation_from_output(self, stdout, stderr):
        """Extract an attestation document from command output"""
        combined_output = f"{stdout}\n{stderr}"
        
        # Look for JSON-shaped blocks containing PCRs or attestation document
        try:
            # Find all potential JSON blocks
            json_pattern = r'(\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\})'
            for match in re.finditer(json_pattern, combined_output):
                json_str = match.group(1)
                try:
                    json_obj = json.loads(json_str)
                    
                    # Check if this looks like an attestation document
                    if isinstance(json_obj, dict) and any(key in json_obj for key in ["pcrs", "nonce", "platform", "attestation_doc"]):
                        logger.info("Found attestation document in command output")
                        return json_obj
                except json.JSONDecodeError:
                    continue
        except Exception as e:
            logger.warning(f"Error extracting PCR-containing document: {e}")
        
        return None
class MockKmsService(KmsService):
    """
    Mock KMS service for testing and simulation.
    This service simulates AWS KMS operations without making actual AWS calls.
    """
    
    def __init__(self, enclave_id=None):
        """
        Initialize the mock KMS service
        
        Args:
            enclave_id (str, optional): The enclave ID to use. If not provided, a new one will be generated.
        """
        logger.info("Creating MockKmsService")
        
        # Generate or use provided enclave ID
        self.enclave_id = enclave_id or str(uuid.uuid4())
        logger.info(f"Initialized MockKmsService with enclave ID: {self.enclave_id}")
        
        # Initialize mock AWS credentials
        self.aws_credentials = {
            "region": "us-east-1",
            "key_id": None
        }
        
        # Initialize mock cryptographic components
        self.init_crypto()
    
    def update_credentials(self, credentials):
        """Update the stored AWS credentials"""
        if not credentials:
            logger.warning("No credentials provided to update")
            return False
            
        self.aws_credentials["region"] = credentials.get('region', self.aws_credentials["region"])
        self.aws_credentials["key_id"] = credentials.get('key_id', self.aws_credentials["key_id"])
        
        logger.info(f"Updated mock AWS credentials. Region: {self.aws_credentials['region']}, Key ID set: {'Yes' if self.aws_credentials['key_id'] else 'No'}")
        
        return True
    
    def decrypt_data(self, encrypted_data, key_id=None, region=None, credentials=None):
        """Mock decryption operation"""
        # Use class-level credentials if not overridden
        if key_id is None:
            key_id = self.aws_credentials["key_id"]
        if region is None:
            region = self.aws_credentials["region"]
            
        logger.info(f"Mock decrypt operation with key_id: {key_id}")
        
        # For mock, we'll just return a placeholder
        cleartext = base64.b64encode(
            f"Decrypted with mock KMS: {encrypted_data[:10]}...".encode('utf-8')
        ).decode('utf-8')
        
        return {
            "operation": "decrypt",
            "result": {
                "data": cleartext,
                "key_id": key_id or "mock-key-id",
            },
            "success": True
        }
    
    def generate_key(self, key_id=None, key_spec="AES_256", region=None, credentials=None):
        """Mock key generation operation"""
        # Use class-level credentials if not overridden
        if key_id is None:
            key_id = self.aws_credentials["key_id"]
        if region is None:
            region = self.aws_credentials["region"]
            
        logger.info(f"Mock genkey operation with key_id: {key_id}, key_spec: {key_spec}")
        
        # Generate a random key based on key_spec
        key_size = 32  # Default for AES_256
        if key_spec == "AES_128":
            key_size = 16
        
        # Generate random key material
        key_bytes = os.urandom(key_size)
        
        return {
            "operation": "genkey",
            "result": {
                "plaintext": base64.b64encode(key_bytes).decode('utf-8'),
                "ciphertext": base64.b64encode(
                    f"Encrypted key from mock KMS for {key_id}".encode('utf-8')
                ).decode('utf-8'),
                "key_id": key_id or "mock-key-id",
                "key_spec": key_spec
            },
            "success": True
        }
    
    def generate_random(self, length=32, region=None, credentials=None):
        """Mock random generation operation"""
        # Use class-level region if not overridden
        if region is None:
            region = self.aws_credentials["region"]
            
        logger.info(f"Mock genrandom operation, length: {length}")
        
        # Generate random bytes
        random_bytes = os.urandom(length)
        
        return {
            "operation": "genrandom",
            "result": {
                "data": base64.b64encode(random_bytes).decode('utf-8'),
                "length": length
            },
            "success": True
        }
    
    def generate_attestation(self, nonce=None, region=None, credentials=None):
        """Generate a mock attestation document for testing"""
        # Use class-level region if not overridden
        if region is None:
            region = self.aws_credentials["region"]
            
        if nonce is None:
            nonce = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
        
        logger.info(f"Generating mock attestation with nonce: {nonce}")
        
        # Get current timestamp
        current_time = int(time.time())
        
        # Check if we're in debug mode
        debug_mode = os.environ.get('DEBUG', 'false').lower() in ('true', '1', 'yes')
        
        # Create PCR values - in debug mode, PCR0 would be all zeros
        pcr0 = base64.b64encode(bytes(32)).decode('utf-8') if debug_mode else base64.b64encode(os.urandom(32)).decode('utf-8')
        
        # Create a realistic mock attestation document
        attestation_doc = {
            # Document metadata
            "version": "1.0",
            "enclave_id": self.enclave_id,
            
            # Timestamps for validity period
            "timestamp": current_time,
            "not_before": current_time - 300,  # Valid from 5 minutes ago
            "not_after": current_time + 86400,  # Valid for 24 hours
            
            # Enclave measurements (PCRs)
            "pcrs": {
                "PCR0": pcr0,  # Image measurement (all zeros in debug mode)
                "PCR1": base64.b64encode(os.urandom(32)).decode('utf-8'),  # Kernel measurement
                "PCR2": base64.b64encode(os.urandom(32)).decode('utf-8'),  # Boot measurement
                "PCR3": base64.b64encode(os.urandom(32)).decode('utf-8'),  # Additional measurement
            },
            
            # Platform information
            "platform": {
                "instance_id": f"i-{uuid.uuid4().hex[:8]}",
                "instance_type": "c5.xlarge",
                "region": region,
                "platform_version": "1.0"
            },
            
            # Nonce provided by the caller for freshness
            "nonce": nonce,
        }
        
        # Generate a proper base64-encoded signature
        signature_data = json.dumps(attestation_doc, sort_keys=True).encode('utf-8')
        signature = self.sign_data(signature_data)
        attestation_doc["signature"] = signature
        
        # Create the full response with the attestation document and public key
        response = {
            "attestation_doc": attestation_doc,
            "public_key": self.public_key,  # Use the actual PEM-formatted public key
            "timestamp": current_time,
            "enclave_id": self.enclave_id,
            "is_mock": True
        }
        
        return response

    def init_crypto(self):
        """Initialize mock cryptographic components"""
        # Generate a mock RSA key pair for signing
        self.private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
        
        # Get the public key in PEM format
        self.public_key = self.private_key.public_key().public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode('utf-8')
        
        logger.info("Initialized mock cryptographic components")
        
        return {
            "public_key_pem": self.public_key,
            "nsm_available": False
        }
    
    def sign_data(self, data, region=None, credentials=None):
        """
        Sign data using the mock private key
        
        Args:
            data: Data to sign (bytes)
            region: AWS region (optional, ignored in mock)
            credentials: AWS credentials (optional, ignored in mock)
            
        Returns:
            str: Base64-encoded signature
        """
        try:
            # If no private key is available, generate one
            if not hasattr(self, 'private_key'):
                self.init_crypto()
            
            # Sign the data using the private key
            if hasattr(self, 'private_key'):
                from cryptography.hazmat.primitives import hashes
                from cryptography.hazmat.primitives.asymmetric import padding
                
                signature = self.private_key.sign(
                    data,
                    padding.PSS(
                        mgf=padding.MGF1(hashes.SHA256()),
                        salt_length=padding.PSS.MAX_LENGTH
                    ),
                    hashes.SHA256()
                )
                
                return base64.b64encode(signature).decode('utf-8')
            
            # Fall back to a mock signature if no private key is available
            logger.warning("No private key available for mock signing")
            return base64.b64encode(b"mock_signature").decode('utf-8')
            
        except Exception as e:
            logger.error(f"Error in mock signing: {e}")
            logger.error(traceback.format_exc())
            # Return a mock signature in case of error
            return base64.b64encode(b"mock_signature_error").decode('utf-8')

def create_kms_service(env_setup: str = None):
    """
    Create the appropriate KMS service based on environment
    
    Args:
        env_setup (str, optional): Environment setup ('SIM' or 'NITRO'). 
                                 If None, reads from ENV_SETUP environment variable.
    
    Returns:
        KmsService: The appropriate KMS service instance
    """
    if env_setup is None:
        env_setup = os.environ.get('ENV_SETUP', 'SIM').upper()
    
    if env_setup == 'NITRO':
        logger.info("Creating RealKmsService")
        return RealKmsService()
    else:
        logger.info("Creating MockKmsService")
        return MockKmsService() 