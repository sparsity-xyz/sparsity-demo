FLEET_URI ?= sparsityxyz/fleet:20250421141233
BRIDGE_URI ?= sparsityxyz/bridge:20250421142445

.PHONY: help build-sim run-sim stop-sim clean-sim logs-sim shell-parent shell-enclave test-sim status-sim build-enclave package-enclave deploy-enclave setup-ec2 generate-aws-credentials

fleet-clear-er-ports:
	@PORT_START=30000; \
	PORT_END=30005; \
	for PORT in $$(seq $$PORT_START $$PORT_END); do \
		CONTAINER_ID=$$(docker ps --format '{{.ID}}' | while read ID; do \
			docker port "$$ID" 2>/dev/null | grep -q ":$$PORT$$" && echo "$$ID"; \
		done); \
		if [ -n "$$CONTAINER_ID" ]; then \
			echo "Port $$PORT is used by container $$CONTAINER_ID. Killing it..."; \
			docker kill "$$CONTAINER_ID"; \
		else \
			echo "Port $$PORT is not used by any Docker container."; \
		fi; \
	done

fleet-start:
	$(MAKE) fleet-clear-er-ports
	docker compose up fleet-run

bridge-start:
	docker compose up bridge
