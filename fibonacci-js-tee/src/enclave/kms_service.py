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
from datetime import datetime, timedelta
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from abc import ABC, abstractmethod
import cbor2
from cose.messages import Sign1Message
from cose.keys import EC2Key
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
from typing import Dict, Any, Optional, Tuple, List, Union
import hashlib
from Crypto.Signature import PKCS1_PSS
from Crypto.Hash import SHA384
from eth_utils import keccak
from eth_keys import keys

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('kms-service')

class KmsService(ABC):
    """Abstract base class for KMS service."""
    
    def __init__(self):
        self.private_key = None
        self.public_key = None
        self.nsm_util = None
        self._init_crypto()
    
    @abstractmethod
    def _init_crypto(self):
        """Initialize cryptographic components."""
        pass
    
    @abstractmethod
    def decrypt_data(self, ciphertext: bytes) -> bytes:
        """Decrypt data using the private key."""
        pass
    
    @abstractmethod
    def generate_key(self) -> Tuple[bytes, bytes]:
        """Generate a new key pair."""
        pass
    
    @abstractmethod
    def sign_data(self, data: bytes) -> bytes:
        """Sign data using the private key."""
        pass
    
    @abstractmethod
    def generate_attestation(self, nonce: Optional[bytes] = None) -> bytes:
        """Generate an attestation document.
        
        Args:
            nonce: Optional nonce to include in the attestation document.
            
        Returns:
            bytes: The attestation document
        """
        pass

class RealKmsService(KmsService):
    """Real KMS service implementation using AWS KMS."""
    
    def _init_crypto(self):
        """Initialize cryptographic components."""
        try:
            from nsm_wrapper.nsm_util import NSMUtil
            self.nsm_util = NSMUtil()
            logger.info("Successfully initialized NSMUtil")
        except Exception as e:
            logger.error(f"Failed to initialize NSMUtil: {e}")
            raise
    
    def decrypt_data(self, ciphertext: bytes) -> bytes:
        """Decrypt data using AWS KMS."""
        return self.nsm_util.decrypt(ciphertext)
    
    def generate_key(self) -> Tuple[bytes, bytes]:
        """Generate a new key pair using AWS KMS."""
        return self.nsm_util.generate_key()
    
    def sign_data(self, data: bytes) -> bytes:
        """Sign data using AWS KMS."""
        return self.nsm_util.sign_data(data)
    
    def generate_attestation(self, nonce: Optional[bytes] = None) -> bytes:
        """Generate an attestation document using the NSM."""
        attestation_doc = self.nsm_util.get_attestation_doc()
        if not attestation_doc:
            raise RuntimeError("Failed to get attestation document from NSM")
        return attestation_doc

class MockKmsService(KmsService):
    """Mock KMS service implementation for testing."""
    
    def _init_crypto(self):
        """Initialize mock cryptographic components using deterministic keys."""
        # In the container, keys are at /app/keys/
        keys_dir = '/app/keys'
        key_info_path = os.path.join(keys_dir, 'key_info.json')
        
        if not os.path.exists(key_info_path):
            logger.error(f"Mock keys not found at {keys_dir}. Please ensure keys are mounted correctly.")
            raise RuntimeError(f"Mock keys not found at {keys_dir}")
        
        try:
            # Load the enclave private key - should be RSA key for NSM compatibility
            with open(os.path.join(keys_dir, 'enclave_key.pem'), 'rb') as f:
                key_data = f.read()
                self.private_key = serialization.load_pem_private_key(
                    key_data,
                    password=None
                )
            self.public_key = self.private_key.public_key()
            
            # Load the enclave app key for signing data
            with open(os.path.join(keys_dir, 'enclave_app_key.pem'), 'rb') as f:
                key_data = f.read()
                self.app_private_key = serialization.load_pem_private_key(
                    key_data,
                    password=None
                )
            self.app_public_key = self.app_private_key.public_key()
            
            # Verify the key is an RSA key
            if not isinstance(self.private_key, rsa.RSAPrivateKey):
                logger.warning("Loaded key is not an RSA key. NSM uses RSA keys for signing.")
            
            # Load certificates
            with open(os.path.join(keys_dir, 'root_cert.pem'), 'rb') as f:
                self.root_cert = x509.load_pem_x509_certificate(f.read())
            with open(os.path.join(keys_dir, 'intermediate1_cert.pem'), 'rb') as f:
                self.int1_cert = x509.load_pem_x509_certificate(f.read())
            with open(os.path.join(keys_dir, 'intermediate2_cert.pem'), 'rb') as f:
                self.int2_cert = x509.load_pem_x509_certificate(f.read())
            with open(os.path.join(keys_dir, 'enclave_cert.pem'), 'rb') as f:
                self.enclave_cert = x509.load_pem_x509_certificate(f.read())
                
            logger.info("Successfully loaded mock keys and certificates")
        except Exception as e:
            logger.error(f"Failed to load mock keys: {e}")
            raise
    
    def decrypt_data(self, ciphertext: bytes) -> bytes:
        """Decrypt data using ECIES with SECP256K1."""
        try:
            # Extract the raw private key bytes in the format expected by eciespy
            private_key_hex = hex(self.private_key.private_numbers().private_value)[2:]
            if len(private_key_hex) < 64:  # Ensure proper padding
                private_key_hex = '0' * (64 - len(private_key_hex)) + private_key_hex
                
            # Decrypt using ECIES
            plaintext = eciespy.decrypt(private_key_hex, ciphertext)
            return plaintext
        except Exception as e:
            logger.error(f"Error in ECIES decryption: {e}")
            logger.error(traceback.format_exc())
            raise
    
    def generate_key(self) -> Tuple[bytes, bytes]:
        """Generate a deterministic SECP256K1 key pair for Ethereum compatibility."""
        # Use deterministic seed for testing predictability
        seed = f"session-{int(time.time())}"
        
        # Generate a SECP256K1 key
        private_key = ec.generate_private_key(
            ec.SECP256K1(),
            default_backend()
        )
        
        # Export the keys in the correct format
        private_bytes = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        
        public_bytes = private_key.public_key().public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        
        return private_bytes, public_bytes
    
    def sign_data(self, data: bytes) -> bytes:
        """Sign data using ECDSA with secp256k1 (Ethereum compatible)."""
        try:
            # Extract raw private key bytes for eth_keys compatibility
            private_bytes = self.app_private_key.private_numbers().private_value.to_bytes(32, byteorder='big')
            eth_private_key = keys.PrivateKey(private_bytes)
            
            # Generate hash using keccak256 directly on the raw bytes
            message_hash = keccak(data)
            
            # Sign the message hash using eth_keys
            signature = eth_private_key.sign_msg_hash(message_hash)
            sig_bytes = signature.to_bytes()
            
            # Extract components
            r = sig_bytes[:32]
            s = sig_bytes[32:64]
            v = sig_bytes[64:]
            v_int = int.from_bytes(v, byteorder='big')
            
            # For Ethereum compatibility, make sure v is 27/28 instead of 0/1
            if v_int < 27 and v_int <= 1:
                v_adjusted = bytes([v_int + 27])
                ethereum_sig = r + s + v_adjusted
            else:
                ethereum_sig = sig_bytes
            
            # Return the complete signature
            return ethereum_sig
            
        except Exception as e:
            logger.error(f"Error in secp256k1 signing: {e}")
            logger.error(traceback.format_exc())
            raise
    
    def generate_attestation(self, nonce: Optional[bytes] = None) -> bytes:
        """Generate a deterministic mock attestation document that matches NSM format."""
        # Create deterministic PCRs
        pcrs = {}
        for i in range(16):
            pcr_data = f"deterministic-pcr-{i}".encode('utf-8')
            pcr_hash = hashlib.sha384(pcr_data).digest()
            pcrs[i] = pcr_hash
        
        # Create module_id as hex string
        module_id = hashlib.sha256(b"mock-module-id").hexdigest()
        
        # Create attestation document payload
        current_time = int(time.time() * 1000)  # Convert to milliseconds
        payload = {
            "module_id": module_id,  # Now a hex string instead of bytes
            "digest": "SHA384",
            "timestamp": current_time,
            "pcrs": pcrs,
            "certificate": self.enclave_cert.public_bytes(serialization.Encoding.DER),
            "cabundle": [
                self.root_cert.public_bytes(serialization.Encoding.DER),
                self.int1_cert.public_bytes(serialization.Encoding.DER),
                self.int2_cert.public_bytes(serialization.Encoding.DER)
            ],
            "public_key": self.app_public_key.public_bytes(
                encoding=serialization.Encoding.DER,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            ),
            "user_data": None,
            "nonce": None
        }
        
        # Convert payload to CBOR
        cbor_payload = cbor2.dumps(payload)
        
        # Create COSE Sign1 message with deterministic kid
        protected_header = {
            1: -35  # alg: ES384
        }
        
        # Get the raw private key value
        private_key_value = self.private_key.private_numbers().private_value.to_bytes(48, 'big')
        
        # Create a COSE key from the raw bytes
        cose_key = EC2Key(
            crv=2,  # P-384
            d=private_key_value,
            x=self.public_key.public_numbers().x.to_bytes(48, 'big'),
            y=self.public_key.public_numbers().y.to_bytes(48, 'big')
        )
        
        # Create and sign the COSE_Sign1 message
        msg = Sign1Message(
            phdr=protected_header,
            payload=cbor_payload
        )
        msg.key = cose_key
        
        # The NSM format expects: [protected headers, unprotected headers, payload, signature]
        # We need to manually construct this format
        signed_msg = msg.encode()
        
        # Decode the signed message to get its components
        decoded = cbor2.loads(signed_msg)
        
        # Construct the final NSM format and tag it with 0xD2 (18)
        final_doc = cbor2.dumps(cbor2.CBORTag(18, [
            decoded.value[0],  # protected headers
            decoded.value[1],  # unprotected headers
            cbor_payload,      # payload
            decoded.value[3]   # signature
        ]))
        
        return final_doc

def create_kms_service(env_setup=None):
    """
    Create the appropriate KMS service based on environment
    
    Args:
        env_setup (str, optional): Environment setup string ('NITRO' or 'SIM').
            If None, will use ENV_SETUP environment variable.
    """
    if env_setup is None:
        env_setup = os.environ.get('ENV_SETUP', 'SIM').upper()
    
    if env_setup == 'NITRO':
        logger.info("Creating RealKmsService")
        return RealKmsService()
    else:
        logger.info("Creating MockKmsService")
        return MockKmsService() 