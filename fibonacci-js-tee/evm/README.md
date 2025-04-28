# Fibonacci JS TEE Smart Contracts

This directory contains the smart contracts for the Fibonacci JS TEE project, which implements a secure and verifiable Fibonacci number calculation system using Trusted Execution Environment (TEE) technology.

## Project Structure

```
contracts/
├── APP.sol              # Main application contract for Fibonacci calculations
├── CertManager.sol      # Certificate verification and management
├── Manager.sol          # Provider and session management
├── NitroValidator.sol   # AWS Nitro attestation validation
├── Outpost.sol          # Bridge between applications and execution providers
├── interfaces/         # Contract interfaces
└── libraries/         # Utility libraries
```

## Smart Contracts Overview

### APP Contract
The main application contract that handles Fibonacci number calculation requests. Key features:
- Manages chat sessions and Fibonacci calculation requests
- Interfaces with the Outpost contract for execution
- Maintains mappings for session management and Fibonacci results
- Provides functions for starting chats and retrieving Fibonacci numbers

### CertManager Contract
Handles certificate verification and management for the TEE system. Key features:
- Manages verified certificates and their metadata
- Provides certificate verification processes
- Stores root CA certificate details
- Includes methods for verifying CA and client certificates

### Manager Contract
Manages providers (both TEE and ER) and session coordination. Key features:
- Handles provider registration and session management
- Maintains mappings for registered providers and session bindings
- Supports both TEE and regular execution environments
- Provides functions for session creation and provider management
- Implements bridge functionality for cross-chain communication

### NitroValidator Contract
Validates AWS Nitro attestations for secure TEE execution. Key features:
- Decodes and validates attestation data structures
- Verifies attestation signatures using ECDSA384
- Validates certificate chains through CertManager
- Processes PCR (Platform Configuration Register) values
- Extracts and verifies public keys from attestations

### Outpost Contract
Acts as a bridge between applications and execution providers. Key features:
- Manages application registration and approval
- Handles session creation and callback management
- Implements security checks and authorization
- Coordinates with the Manager contract for provider selection
- Supports both TEE and regular execution environments

## Deployment

The contracts use the Hardhat Ignition deployment system with proxy support for upgradability. Key deployment files:
- `ignition/modules/APP.ts`: APP contract deployment
- `ignition/modules/CertManager.ts`: CertManager deployment
- `ignition/modules/ManagerProxy.ts`: Manager contract deployment with proxy
- `ignition/modules/OutpostProxy.ts`: Outpost contract deployment with proxy
- `ignition/modules/NitroValidator.ts`: NitroValidator contract deployment

## Usage

The system supports two types of execution environments:
1. Trusted Execution Environment (TEE)
2. Regular Execution Environment (ER)

Applications can request Fibonacci calculations through the APP contract, which coordinates with the Outpost and Manager contracts to execute the calculations in a secure and verifiable manner.
