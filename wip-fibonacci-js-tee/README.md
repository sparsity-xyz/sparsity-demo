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
```json
{
  "enclave_id": "0e5671ac-3f4a-48f3-b6e2-97ffbfce25e8",
  "input": 20,
  "result": 6765,
  "signature": "Rg6lrhf924Cl9+b843W7YnPi6WALE4FsMv737bJBmG1i+e3a1XhjSIB8uXsnjASSk+eSthj+n9K2WStinkQNSGjhOBXGb20PsG09zX6mgzUQgsND3+DzFxPCWmhpyBtE9+PnOdb+j6W1vs8HIN/n5M4K4n2df2ZCSNrgzUu+mZWaW8Xrlfzoe4gVPAVJ5AN/gIaPYReC9zTHq+ES6207T/+xtwGx94WBw1qpjvfZ0jPs90T0DL+Lwghjuwm6tsbDlPiPu3akuKnyF343nAzaEgtZqXV8QjpNIQLYXFWFUnZFOwyd6DeEYGxBvuZLrXnthto5oFcZxEx7HNCqwnFgAQ==",
  "timestamp": 1742365560
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
 
