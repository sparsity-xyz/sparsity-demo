FLEET_URI ?= sparsityxyz/fleet:20250421141233
BRIDGE_URI ?= sparsityxyz/bridge:20250421142445

.PHONY: fleet-clear-er-ports fleet-start bridge-start

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

fleet-start-DHI:
	$(MAKE) fleet-clear-er-ports
	docker compose -f docker-compose-WSL-Mac.yaml up fleet-run

bridge-start:
	docker compose up bridge

bridge-start-DHI:
	docker compose -f docker-compose-WSL-Mac.yaml up bridge
