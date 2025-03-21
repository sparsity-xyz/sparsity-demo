# Makefile for AWS Nitro Enclave Development

# Include environment variables from .env file if it exists
-include .env
export

# Default values for environment variables
ENV_SETUP ?= SIM
ENCLAVE_HOST ?= enclave
ENCLAVE_PORT ?= 8000
PARENT_PORT ?= 8000
AWS_REGION ?= us-east-1
DEBUG ?= false
ENCLAVE_CPU_LIMIT ?= 1
ENCLAVE_MEMORY_LIMIT ?= 512M

# Default EC2 instance alias if not set in .env
EC2_HOST ?= tee-test
EC2_USER ?= ec2-user

.PHONY: help build-sim run-sim stop-sim clean-sim logs-sim shell-parent shell-enclave test-sim status-sim build-enclave package-enclave deploy-enclave setup-ec2 generate-aws-credentials

# Default target
help:
	@echo "AWS Nitro Enclave Development Makefile"
	@echo ""
	@echo "Simulation targets (for local development):"
	@echo "  make build-sim     - Build Docker images for simulation"
	@echo "  make run-sim       - Run the simulator (detached mode)"
	@echo "  make run-sim-fg    - Run the simulator (foreground mode)"
	@echo "  make stop-sim      - Stop the simulator"
	@echo "  make clean-sim     - Stop and remove containers, networks, and images"
	@echo "  make logs-sim      - View logs from all containers"
	@echo "  make shell-parent  - Open a shell in the parent container"
	@echo "  make shell-enclave - Open a shell in the enclave simulator container"
	@echo "  make test-sim      - Run a test simulation"
	@echo "  make status-sim    - Check the status of the simulation containers"
	@echo ""
	@echo "Real deployment targets (for AWS Nitro Enclaves):"
	@echo "  make setup-ec2     - Set up the EC2 instance with required dependencies"
	@echo "  make build-enclave - Build the parent and enclave applications for real deployment"
	@echo "  make package-enclave - Package the enclave application as an EIF file"
	@echo "  make deploy-enclave - Deploy the enclave to a Nitro Enclave-enabled EC2 instance"
	@echo "  make generate-aws-credentials - Generate temporary AWS credentials using STS"
	@echo ""
	@echo "  make help          - Show this help message"
	@echo ""
	@echo "Environment variables (can be set in .env file):"
	@echo "  ENV_SETUP          - Environment setup (SIM or NITRO)"
	@echo "  ENCLAVE_HOST       - Hostname for simulation enclave"
	@echo "  ENCLAVE_PORT       - Port for simulation enclave"
	@echo "  PARENT_PORT        - Port for parent application"
	@echo "  AWS_REGION         - AWS region for KMS operations"
	@echo "  AWS_ACCESS_KEY_ID  - AWS access key ID for authentication"
	@echo "  AWS_SECRET_ACCESS_KEY - AWS secret access key for authentication"
	@echo "  AWS_SESSION_TOKEN  - AWS session token for temporary credentials"
	@echo "  KMS_KEY_ID         - KMS key ID for encryption/decryption"
	@echo "  DEBUG              - Enable debug mode (true/false)"
	@echo "  ENCLAVE_CPU_LIMIT  - CPU limit for enclave simulation"
	@echo "  ENCLAVE_MEMORY_LIMIT - Memory limit for enclave simulation"
	@echo "  EC2_HOST           - SSH alias or hostname for the EC2 instance"
	@echo "  EC2_USER           - SSH username for the EC2 instance"

# Simulation targets
build-sim:
	@echo "Building Docker images for simulation..."
	docker compose build

run-sim:
	@echo "Starting the simulator in detached mode..."
	docker compose up -d
	@echo "Simulator is running. Use 'make logs-sim' to view logs."
	@echo "Access the parent application at http://localhost:${PARENT_PORT}/simulate"

run-sim-fg:
	@echo "Starting the simulator in foreground mode..."
	docker compose up

stop-sim:
	@echo "Stopping the simulator..."
	docker compose down

clean-sim:
	@echo "Cleaning up containers, networks, and images..."
	docker compose down --rmi all --volumes --remove-orphans

logs-sim:
	@echo "Viewing logs from all containers..."
	docker compose logs -f

logs-parent:
	@echo "Viewing logs from parent container..."
	docker compose logs -f parent

logs-enclave:
	@echo "Viewing logs from enclave simulator container..."
	docker compose logs -f enclave

shell-parent:
	@echo "Opening shell in parent container..."
	docker compose exec parent /bin/bash

shell-enclave:
	@echo "Opening shell in enclave simulator container..."
	docker compose exec enclave /bin/bash

# Real deployment targets
build-enclave:
	@echo "Building applications for real deployment..."
	
	# Build the parent application Docker image
	docker build -t nitro-parent:latest -f docker/Dockerfile.parent .
	
	# Build the enclave application Docker image
	docker build -t nitro-enclave:latest -f docker/Dockerfile.enclave .
	
	# Save the enclave image to a tar file
	mkdir -p build
	docker save nitro-enclave:latest > build/nitro-enclave.tar
	
	@echo "Docker images built successfully and saved to build/nitro-enclave.tar"
	@echo "You can now run 'make package-enclave' to create the EIF file"

package-enclave:
	@echo "Packaging enclave application as EIF..."
	@if [ ! -f build/nitro-enclave.tar ]; then \
		echo "Error: Enclave image not found. Run 'make build-enclave' first."; \
		exit 1; \
	fi
	
	# Copy the enclave image to the EC2 instance
	scp build/nitro-enclave.tar $(EC2_HOST):/tmp/nitro-enclave.tar
	
	# Copy the packaging script to the EC2 instance
	scp scripts/package_enclave.sh $(EC2_HOST):/tmp/package_enclave.sh
	
	# Run the packaging script and remove it after execution
	ssh $(EC2_HOST) "chmod +x /tmp/package_enclave.sh && /tmp/package_enclave.sh && rm /tmp/package_enclave.sh"
	
	@echo "Enclave Image File (EIF) created successfully on the EC2 instance"
	@echo "You can now run 'make deploy-enclave' to deploy the enclave"

# Deploy enclave to remote EC2 instance
deploy-enclave:
	@echo "Generating AWS credentials file using jq..."
	@jq -n \
		--arg access_key "$(AWS_ACCESS_KEY_ID)" \
		--arg secret_key "$(AWS_SECRET_ACCESS_KEY)" \
		--arg region "$(AWS_REGION)" \
		--arg kms_key "$(KMS_KEY_ID)" \
		--arg session_token "$(AWS_SESSION_TOKEN)" \
		'{aws_access_key_id: $$access_key, aws_secret_access_key: $$secret_key, region: $$region, kms_key_id: $$kms_key, aws_session_token: $$session_token}' > aws_credentials.json
	
	@echo "Preparing files for EC2 instance..."
	# Create a directory for the app structure
	ssh $(EC2_HOST) "mkdir -p /home/ec2-user/app/src/parent /home/ec2-user/app/src/enclave"
	
	@echo "Copying files to EC2 instance..."
	scp build/nitro-enclave.tar scripts/deploy_enclave.sh aws_credentials.json $(EC2_USER)@$(EC2_HOST):/home/ec2-user/
	
	@echo "Copying source code to EC2 instance..."
	scp -r src/parent/* $(EC2_HOST):/home/ec2-user/app/src/parent/
	
	@echo "Removing local credentials file..."
	rm aws_credentials.json
	
	@echo "Running deployment script on EC2 instance..."
	ssh $(EC2_HOST) "bash /home/ec2-user/deploy_enclave.sh"

setup-ec2:
	@echo "Setting up EC2 instance for Nitro Enclaves..."
	scp scripts/setup_ec2.sh $(EC2_HOST):/tmp/setup_ec2.sh
	ssh $(EC2_HOST) "chmod +x /tmp/setup_ec2.sh && /tmp/setup_ec2.sh && rm /tmp/setup_ec2.sh"
	@echo "EC2 instance setup complete. You may need to reconnect to the instance."
	@echo "After reconnecting, you can run 'make package-enclave' to create the EIF file."

# Get temporary AWS credentials using STS
generate-aws-credentials:
	@echo $(shell aws sts get-session-token --query 'Credentials' | jq -r '.AccessKeyId, .SecretAccessKey, .SessionToken')