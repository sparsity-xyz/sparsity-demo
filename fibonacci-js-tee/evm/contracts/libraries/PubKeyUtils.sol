// SPDX-License-Identifier: MIT
pragma solidity ^0.8.15;

import {CborElement, CborDecode, LibCborElement} from "./CborDecode.sol";
import {LibBytes} from "./LibBytes.sol";

import {console} from "hardhat/console.sol";

/// @title PubKeyUtils
/// @notice Library for extracting public keys and deriving Ethereum addresses
library PubKeyUtils {
    using LibBytes for bytes;
    using LibCborElement for CborElement;

    /// @notice Extracts a public key from a CBOR element in an attestation document
    /// @param attestation The full attestation document bytes
    /// @param publicKey The CBOR element containing the public key
    /// @return The extracted public key bytes
    function extractPublicKeyFromCbor(bytes memory attestation, CborElement publicKey) 
        internal pure returns (bytes memory) 
    {
        // Use the CborDecode.slice function to extract bytes from the CBOR element
        bytes memory rawPubKey = CborDecode.slice(attestation, publicKey);
        
        // The exact pattern we need to look for based on the example:
        // 0x04 + 32 bytes X + 32 bytes Y
        
        // First, search for the secp256k1 OID pattern "052b8104000a"
        for (uint i = 0; i < rawPubKey.length - 6; i++) {
            if (i + 6 < rawPubKey.length && 
                rawPubKey[i] == 0x05 && 
                rawPubKey[i+1] == 0x2b && 
                rawPubKey[i+2] == 0x81 &&
                rawPubKey[i+3] == 0x04 && 
                rawPubKey[i+4] == 0x00 && 
                rawPubKey[i+5] == 0x0a) {
                
                // After the OID, expect "03420004" pattern which leads to the key
                if (i + 11 < rawPubKey.length &&
                    rawPubKey[i+6] == 0x03 &&
                    rawPubKey[i+7] == 0x42 &&
                    rawPubKey[i+8] == 0x00 &&
                    rawPubKey[i+9] == 0x04) {
                    
                    // Found the marker for the uncompressed key (0x04)
                    uint keyPos = i + 9;
                    
                    // Make sure we have enough bytes for a full 65-byte key
                    if (keyPos + 65 <= rawPubKey.length) {
                        bytes memory cleanPubKey = new bytes(65);
                        for (uint j = 0; j < 65; j++) {
                            cleanPubKey[j] = rawPubKey[keyPos + j];
                        }
                        return cleanPubKey;
                    }
                }
            }
        }
        
        // Last resort - just return the raw key
        return rawPubKey;
    }

    /// @notice Derives an Ethereum address from a public key
    /// @param publicKey The public key in any supported format
    /// @return The derived Ethereum address
    function deriveAddressFromPublicKey(bytes memory publicKey) 
        internal pure returns (address) 
    {
        // For uncompressed public keys, we need to skip the first byte (0x04)
        bytes memory strippedKey;
        
        if (publicKey.length == 65 && publicKey[0] == 0x04) {
            // Uncompressed public key format (0x04 + x + y)
            strippedKey = new bytes(64);
            for (uint i = 0; i < 64; i++) {
                strippedKey[i] = publicKey[i + 1];
            }
        } else if (publicKey.length == 64) {
            // Already in the right format - just x and y coordinates
            strippedKey = publicKey;
        } else {
            // Try to handle DER-encoded keys or other formats
            uint offset = 0;
            
            // If the key starts with a sequence tag (0x30 in DER)
            if (publicKey.length > 0 && publicKey[0] == 0x30) {
                // Skip sequence tag and length
                offset = 2;
                
                // Skip OID for algorithm
                if (offset < publicKey.length && publicKey[offset] == 0x06) {
                    offset += 2 + uint8(publicKey[offset + 1]);
                }
                
                // Find the bit string containing the key
                if (offset < publicKey.length && publicKey[offset] == 0x03) {
                    offset += 2; // Skip tag and length
                    offset += 1; // Skip unused bits byte
                    
                    // Now we should be at the EC point
                    if (offset < publicKey.length && publicKey[offset] == 0x04) {
                        // Skip the uncompressed point marker
                        offset += 1;
                        
                        // Extract the 64 bytes (x and y)
                        uint bytesToExtract = publicKey.length - offset;
                        if (bytesToExtract >= 64) bytesToExtract = 64;
                        
                        strippedKey = new bytes(bytesToExtract);
                        for (uint i = 0; i < bytesToExtract; i++) {
                            strippedKey[i] = publicKey[i + offset];
                        }
                    }
                }
            }
            
            // If we couldn't parse it using the logic above
            if (strippedKey.length == 0) {
                // Fallback - try to use the raw key
                strippedKey = publicKey;
            }
        }
        
        // Hash the public key bytes and take the last 20 bytes as the address
        bytes32 hash = keccak256(strippedKey);
        return address(uint160(uint256(hash)));
    }

    /// @notice Validates a signature against a public key
    /// @param messageHash Hash of the message that was signed
    /// @param signature The signature in Ethereum format (65 bytes: r, s, v)
    /// @param publicKey The public key to verify against
    /// @return True if the signature is valid, false otherwise
    function verifySignature(bytes32 messageHash, bytes memory signature, bytes memory publicKey) 
        internal pure returns (bool) 
    {
        // Extract r, s, v from the signature
        require(signature.length == 65, "Invalid signature length");
        
        bytes memory pubKeyXY;
        
        // Ensure the public key is in the correct format (0x04 + X + Y)
        if (publicKey.length >= 65 && publicKey[0] == 0x04) {
            // Standard uncompressed key format - we need 64 bytes of X and Y coords
            pubKeyXY = new bytes(64);
            for (uint i = 0; i < 64 && i + 1 < publicKey.length; i++) {
                pubKeyXY[i] = publicKey[i + 1]; // Skip the 0x04 prefix
            }
        } else {
            // Try to use the public key as is
            pubKeyXY = publicKey;
        }
        
        // Hash the key to get Ethereum address
        bytes32 pkHash = keccak256(pubKeyXY);
        address derivedAddress = address(uint160(uint256(pkHash)));
        
        // Extract r, s, v from the signature
        bytes32 r;
        bytes32 s;
        uint8 v;
        
        assembly {
            r := mload(add(signature, 32))
            s := mload(add(signature, 64))
            v := byte(0, mload(add(signature, 96)))
        }
        
        // Adjust v for Ethereum's encoding
        if (v < 27) {
            v += 27;
        }
        
        // Standard Ethereum signature recovery
        address recoveredAddress = ecrecover(messageHash, v, r, s);
        
        // Compare the recovered address with the derived address
        return recoveredAddress == derivedAddress;
    }
}