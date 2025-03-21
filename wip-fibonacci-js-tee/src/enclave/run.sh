#!/bin/bash

# This script starts the enclave application with the correct environment setup

# Set defaults if not provided
export ENV_SETUP=${ENV_SETUP:-SIM}
export ENCLAVE_PORT=${ENCLAVE_PORT:-8000}
export APP_TYPE=${APP_TYPE:-STANDARD}
export CREATION_METHOD=${CREATION_METHOD:-AUTO}
# Go to the enclave directory
cd /app/enclave

python3 simple_enclave_app.py