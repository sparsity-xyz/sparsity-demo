# TEE (Trusted Execution Environment) Demo - Alpha Version

A simple demonstration of a Trusted Execution Environment using AWS Nitro Enclaves. This project includes a simulation mode for local development and testing.

## Prerequisites

- Docker and Docker Compose
- Python 3.12 (for local development)

## Project Structure

```
.
├── docker/
│   ├── Dockerfile.enclave_sim    # Enclave container for simulation
│   └── Dockerfile.parent        # Parent container for simulation
├── src/
│   ├── enclave/                 # Enclave application code
│   │   ├── base_enclave_app.py  # Base enclave application
│   │   ├── kms_service.py       # KMS service implementation
│   │   ├── parent_connector.py  # Parent communication connector
│   │   ├── run.sh              # Enclave startup script
│   │   └── simple_enclave_app.py # Fibonacci calculation app
│   └── parent/                  # Parent application code
│       ├── enclave_connector.py # Enclave communication connector
│       └── parent_app.py        # Parent application
├── docker-compose.yml           # Docker Compose configuration
└── Makefile                    # Build and run commands
```

## Quick Start


1. Build and start the simulation environment:
   ```bash
   make build-sim && make run-sim-fg
   ```

2. Test the Fibonacci calculation:
   ```bash
   curl http://localhost:8000/fibonacci/20
   ```
   or open http://localhost:8000/fibonacci/20 on an internet browser

## Simulation Mode

The simulation mode runs two containers:
- `nitro-enclave`: Simulates the enclave environment
- `nitro-parent`: Simulates the parent application

The enclave provides a simple Fibonacci calculation endpoint, along with the base endpoints:
 - `GET /fibonacci/<n>`: Calculate the nth Fibonacci number
 - `GET /attest`: get attestation document (mock)
 - `GET /health`: get status of the enclave

Example response:
### `GET /fibonacci/20`
```json
{
  "enclave_id": "0e5671ac-3f4a-48f3-b6e2-97ffbfce25e8",
  "input": 20,
  "result": 6765,
  "signature": "Rg6lrhf924Cl9+b843W7YnPi6WALE4FsMv737bJBmG1i+e3a1XhjSIB8uXsnjASSk+eSthj+n9K2WStinkQNSGjhOBXGb20PsG09zX6mgzUQgsND3+DzFxPCWmhpyBtE9+PnOdb+j6W1vs8HIN/n5M4K4n2df2ZCSNrgzUu+mZWaW8Xrlfzoe4gVPAVJ5AN/gIaPYReC9zTHq+ES6207T/+xtwGx94WBw1qpjvfZ0jPs90T0DL+Lwghjuwm6tsbDlPiPu3akuKnyF343nAzaEgtZqXV8QjpNIQLYXFWFUnZFOwyd6DeEYGxBvuZLrXnthto5oFcZxEx7HNCqwnFgAQ==",
  "timestamp": 1742365560
}
```

### `GET /attest`
```json
{
  "attestation": {
    "attestation_doc": {
      "enclave_id": "a04e44a6-928c-4ddd-8416-258813e152c7",
      "nonce": "UlmhZucTy9ecBZfE",
      "not_after": 1742745784,
      "not_before": 1742659084,
      "pcrs": {
        "PCR0": "HYt8dFXCgy8iYaHwWu/m51Puyc1nSbyMHAjXelt23DM=",
        "PCR1": "YWOm+P0CbxkHZW2SP3p8xFtnKpJtL5VvPO5gNS0v4UU=",
        "PCR2": "lYxipTgX7HcxJCjTPywYo0vkFtlyxcVQZDTSCeGJWqc=",
        "PCR3": "u+wlB9r0ZPM/e7pmXM+CfrMGpguvmPGv96XN+vjTPww="
      },
      "platform": {
        "instance_id": "i-0e157a00",
        "instance_type": "c5.xlarge",
        "platform_version": "1.0",
        "region": "us-east-1"
      },
      "signature": "hOgIrkwM5zAFlcXgGCyWKodu5BRfqNxR2dlGgDkT5n3+gZcxr0/+jj1rodCfXjuVWEtB60VCZ3lMk/+tmwqDqh40gdYKn6JNkqQQnnUqRG5O6TmRvBeMhooLgndQ6CIhcxRyHuI7Xs50A4v+jHg8V7JI9vu8EwsciIXG6zidaD9EPKAoZEJXwnr+twPlcDIQ2GxWchkZCrR7at3zxYPTDTU5pzkzc/AeNMK6RQktcRiYZ13PPkSWDjYmMCGev51flJattmLFgOOrUlMtauq07iipkHXOSIc3ICdm3UfgeDi7Pq0TPoGXwtvzbf/9tS0FuAXGfM5eqsEioJOuLowNwA==",
      "timestamp": 1742659384,
      "version": "1.0"
    },
    "enclave_id": "a04e44a6-928c-4ddd-8416-258813e152c7",
    "is_mock": true,
    "public_key": "-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA1OBYw/jv3LZ3vTvrtck3\n80VGLw/z9/k0fMI5mlHtNMfnT7if6h5Wawr1yLWtDB9SRbFw4k+UCpob+MxLtCmk\nFBWJ8L7wmxZ0Firszh22d6snYLJ40u13BFWTdry52vvEzNf4G6pLLksZ2escP9mZ\nI3qHSYXEtuS+Zlq6XcWz3mADbxFbEg18F3PRglTHtJ3rCj7XOE7orE55f9GbQR8g\nz0eIvZAYv/i4TUvdaha/K4uXMzlIBNRkqjW1EJAApn3kLfd6sBPZ0AB9415rOPxp\nPTuEw94domZNaQR1mglUIbyNR5jdPHcMgaCl8VtTakmS/z1EzrBTuIKCtvj+YUrK\njQIDAQAB\n-----END PUBLIC KEY-----\n",
    "timestamp": 1742659384
  },
  "nonce": "UlmhZucTy9ecBZfE",
  "status": "success"
}
```

### `GET /health`
```json
{
  "debug_mode": false,
  "enclave_id": "a04e44a6-928c-4ddd-8416-258813e152c7",
  "signature": "hFszpb4CzmYS2R6qwWAfp8mEBimz9iNQiSUL7Zte06E0K4+l5sxU7CpFdt3SryP2O1Lu/B7JRqh2nBCXrRYMRDqTdC8UJjqQ4jxybg28rcx1+VmXfODTBK/9XxoMy+CK5xhKiLCHSDNWuA9n7u/Fb26D0T9J/BUf/E/A/bwuvD3n3fS4RchpREdeKjBKOWEmGvYwmG/9JXVs9RFFftFpHX/cKRuaNjeE1Gu51ZT2l9BPZ92SoVRWGHnMPixnfBNbOUF7FZfgusFuMGJ74ZWhj2Z0khRau9Cx5eZZtJFOnLVYMrS4KwAw6MgLPvqnDgz/rwokiE0eR5euGstqKyHC1g==",
  "status": "healthy",
  "timestamp": 1742659465
}
```

## Development

### Building
 - Edit the enclave application in apps/simple_enclave_app.py for core app logic

 - Use kms_service to interact with the computation verification endpoints

 - Use parent_connector to handle commmmunication with the parent app

### Logs

View logs from both containers:
```bash
docker compose logs -f
```
 
