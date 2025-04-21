#!/usr/bin/env python3

import argparse
import base64
import binascii
import sys
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.serialization import load_der_public_key
import hashlib
from eth_hash.auto import keccak

def is_base64(s):
    try:
        # Check if the string can be decoded as base64
        base64.b64decode(s)
        return True
    except Exception:
        return False

def decode_pubkey(key_data, is_hex=False):
    try:
        # Convert to bytes if necessary
        if is_hex:
            try:
                # Remove '0x' prefix if present
                if key_data.startswith('0x'):
                    key_data = key_data[2:]
                key_bytes = binascii.unhexlify(key_data)
            except binascii.Error:
                print("Error: Invalid hex format")
                return
        else:
            try:
                key_bytes = base64.b64decode(key_data)
            except Exception:
                print("Error: Invalid base64 format")
                return
        
        # Try to load the key
        try:
            public_key = load_der_public_key(key_bytes)
            
            # Check if it's an EC key
            if isinstance(public_key, ec.EllipticCurvePublicKey):
                pub_nums = public_key.public_numbers()
                curve_name = public_key.curve.name
                
                print(f"Algorithm: EC (Curve: {curve_name})")
                print(f"X coordinate (hex): 0x{pub_nums.x:064x}")
                print(f"Y coordinate (hex): 0x{pub_nums.y:064x}")
                
                # For Ethereum compatibility
                uncompressed_bytes = b'\x04' + pub_nums.x.to_bytes(32, 'big') + pub_nums.y.to_bytes(32, 'big')
                print(f"Uncompressed key (hex): 0x{uncompressed_bytes.hex()}")
                
                # Correct Ethereum address calculation: keccak256(pubkey without prefix)[12:]
                # Remove the '04' prefix and compute keccak256 hash
                key_bytes_for_hash = pub_nums.x.to_bytes(32, 'big') + pub_nums.y.to_bytes(32, 'big')
                keccak_hash = keccak(key_bytes_for_hash)
                eth_address = '0x' + keccak_hash[-20:].hex()
                print(f"Ethereum address: {eth_address}")
            else:
                print("Key type not supported. Only EC keys are supported.")
        
        except Exception as e:
            print(f"Error decoding DER key: {str(e)}")
            
            # Attempt to parse manually as a fallback
            print("\nFallback: Manual parsing of DER structure:")
            print(f"Raw DER (hex): 0x{key_bytes.hex()}")
            
            # Locate the OID for secp256k1 or try to find the key data
            secp256k1_oid = bytes.fromhex("2a8648ce3d020106052b8104000a")  # OID for secp256k1
            pos = key_bytes.find(secp256k1_oid)
            
            if pos != -1:
                print(f"Found secp256k1 OID at position {pos}")
                # Look for bitstring marker (0x03) followed by key data
                bitstring_pos = key_bytes.find(b'\x03', pos + len(secp256k1_oid))
                if bitstring_pos != -1 and bitstring_pos + 2 < len(key_bytes):
                    length = key_bytes[bitstring_pos + 1]
                    if bitstring_pos + 2 + length <= len(key_bytes) and key_bytes[bitstring_pos + 2] == 0:
                        # Skip the 0x00 unused bits byte
                        key_part = key_bytes[bitstring_pos + 3:bitstring_pos + 2 + length]
                        print(f"Extracted key data (hex): 0x{key_part.hex()}")
                        if key_part[0] == 0x04 and len(key_part) >= 65:  # Uncompressed key format
                            x_coord = key_part[1:33]
                            y_coord = key_part[33:65]
                            print(f"X coordinate (hex): 0x{x_coord.hex()}")
                            print(f"Y coordinate (hex): 0x{y_coord.hex()}")
                            
                            # Calculate Ethereum address
                            keccak_hash = keccak(x_coord + y_coord)
                            eth_address = '0x' + keccak_hash[-20:].hex()
                            print(f"Ethereum address: {eth_address}")
            
            # Scan for potential uncompressed EC key marker (0x04)
            for i in range(len(key_bytes) - 65):
                if key_bytes[i] == 0x04:
                    potential_key = key_bytes[i:i+65]
                    print(f"Potential uncompressed key at offset {i}: 0x{potential_key.hex()}")
                    x_coord = potential_key[1:33]
                    y_coord = potential_key[33:65]
                    print(f"  X coordinate: 0x{x_coord.hex()}")
                    print(f"  Y coordinate: 0x{y_coord.hex()}")
                    
                    # Calculate Ethereum address
                    keccak_hash = keccak(x_coord + y_coord)
                    eth_address = '0x' + keccak_hash[-20:].hex()
                    print(f"  Ethereum address: {eth_address}")
                    break
    
    except Exception as e:
        print(f"Unexpected error: {str(e)}")

def main():
    parser = argparse.ArgumentParser(description='Decode DER-encoded public keys')
    parser.add_argument('key', help='DER-encoded public key (base64 or hex)')
    parser.add_argument('--hex', action='store_true', help='Treat input as hex (default is base64)')
    
    args = parser.parse_args()
    
    # Auto-detect format if not specified
    if not args.hex and not is_base64(args.key):
        # If it looks like hex, treat it as hex
        if all(c in '0123456789abcdefABCDEF' for c in args.key.replace('0x', '')):
            print("Auto-detected hex format")
            args.hex = True
        else:
            print("Warning: Input doesn't appear to be valid base64 or hex")
    
    decode_pubkey(args.key, args.hex)

if __name__ == "__main__":
    main()