"""
This file is modified based on donkersgoed's repository (https://github.com/donkersgoed/nitropepper-enclave-app)
"""

import Crypto
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization
from eth_utils import keccak
from eth_keys import keys
import ecies

import libnsm

class NSMRandomNumberGenerator:
    """Custom random number generator that uses NSM."""
    
    def __init__(self, nsm_fd):
        self._nsm_fd = nsm_fd
    
    def random_bytes(self, length):
        """Generate random bytes using NSM."""
        return libnsm.nsm_get_random(self._nsm_fd, length) # pylint:disable=c-extension-no-member

class NSMUtil():
    """NSM util class."""

    def __init__(self):
        """Construct a new NSMUtil instance."""
        # Initialize the Rust NSM Library
        self._nsm_fd = libnsm.nsm_lib_init() # pylint:disable=c-extension-no-member
        
        # Create a custom random number generator
        self._rng = NSMRandomNumberGenerator(self._nsm_fd)
        
        # Create a custom backend that uses our RNG
        self._backend = default_backend()
        self._backend._rng = self._rng # pylint:disable=protected-access
        
        # Generate a new SECP256K1 private key
        self._private_key = ec.generate_private_key(
            ec.SECP256K1,
            backend=self._backend
        )
        
        # Export the public key in DER format
        self._public_key = self._private_key.public_key().public_bytes(
            encoding=serialization.Encoding.DER,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        
        # Extract raw private key bytes for eth_keys compatibility
        private_bytes = self._private_key.private_numbers().private_value.to_bytes(32, byteorder='big')
        self._eth_private_key = keys.PrivateKey(private_bytes)
        self._eth_public_key = self._eth_private_key.public_key

    def get_attestation_doc(self):
        """Get the attestation document from /dev/nsm."""
        libnsm_att_doc_cose_signed = libnsm.nsm_get_attestation_doc( # pylint:disable=c-extension-no-member
            self._nsm_fd,
            self._public_key,
            len(self._public_key)
        )
        return libnsm_att_doc_cose_signed
    
    def decrypt(self, ciphertext):
        """
        Decrypt ciphertext using ECIES (Elliptic Curve Integrated Encryption Scheme)
        with SECP256K1 curve (Ethereum compatible)
        
        Args:
            ciphertext: Encrypted data in bytes format
            
        Returns:
            bytes: Decrypted plaintext
        """
        # Extract the raw private key bytes in the format expected by eciespy
        private_key_hex = hex(self._private_key.private_numbers().private_value)[2:]
        if len(private_key_hex) < 64:  # Ensure proper padding
            private_key_hex = '0' * (64 - len(private_key_hex)) + private_key_hex
            
        # Decrypt using ECIES
        plaintext = ecies.decrypt(private_key_hex, ciphertext)
        return plaintext
    
    def sign_data(self, data: bytes) -> bytes:
        """
        Sign data using ECDSA with secp256k1 (Ethereum compatible)
        
        Args:
            data: Data to sign in bytes format
            
        Returns:
            bytes: The signature in Ethereum format (65 bytes: r, s, v)
        """
        # Generate hash using keccak256 directly on the raw bytes
        message_hash = keccak(data)
        
        # Sign the message hash using eth_keys
        signature = self._eth_private_key.sign_msg_hash(message_hash)
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