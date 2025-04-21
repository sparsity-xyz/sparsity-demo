node:
	RUST_LOG="off,sui_node=info" sui start --with-faucet --force-regenesis

faucet:
	sui client faucet

deploy-outpost:
	@if [ "$(verbose)" = "true" ]; then \
		result=$$(sui client publish --gas-budget 50000000 --json outpost); \
	else \
		result=$$(sui client publish --gas-budget 50000000 --json outpost 2>/dev/null); \
	fi; \
	package_id=$$(echo "$$result" | jq -r '.objectChanges[] | select(.type == "published") | .packageId'); \
	admin_cap_id=$$(echo "$$result" | jq -r '.objectChanges[] | select(.type == "created" and (.objectType | type == "string") and (.objectType | contains("::outpost::AdminCap"))) | .objectId'); \
	app_session_id=$$(echo "$$result" | jq -r '.objectChanges[] | select(.type == "created" and (.objectType | type == "string") and (.objectType | contains("::outpost::AppSession"))) | .objectId'); \
	app_registry_id=$$(echo "$$result" | jq -r '.objectChanges[] | select(.type == "created" and (.objectType | type == "string") and (.objectType | contains("::outpost::AppRegistry"))) | .objectId'); \
	echo ""; \
	echo "Outpost Contract Deployed. Environment Variables:"; \
	echo "OUTPOST_ADDR=$$package_id"; \
	echo "OUTPOST_ADMIN_CAP=$$admin_cap_id"; \
	echo "OUTPOST_APP_REGISTRY=$$app_registry_id"; \
	echo "OUTPOST_APP_SESSION=$$app_session_id"; \
	echo "export OUTPOST_ADDR=$$package_id" > .env; \
	echo "export OUTPOST_ADMIN_CAP=$$admin_cap_id" >> .env; \
	echo "export OUTPOST_APP_REGISTRY=$$app_registry_id" >> .env; \
	echo "export OUTPOST_APP_SESSION=$$app_session_id" >> .env

deploy-app:
	@if [ "$(verbose)" = "true" ]; then \
		result=$$(sui client publish --gas-budget 50000000 --json app); \
	else \
		result=$$(sui client publish --gas-budget 50000000 --json app 2>/dev/null); \
	fi; \
	package_id=$$(echo "$$result" | jq -r '.objectChanges[] | select(.type == "published") | .packageId'); \
	app_state_id=$$(echo "$$result" | jq -r '.objectChanges[] | select(.type == "created" and (.objectType | type == "string") and (.objectType | contains("::app::State"))) | .objectId'); \
	echo ""; \
	echo "App Contract Deployed. Environment Variables:"; \
	echo "APP_ADDR=$$package_id"; \
	echo "APP_STATE=$$app_state_id"; \
	echo "export APP_ADDR=$$package_id" >> .env; \
	echo "export APP_STATE=$$app_state_id" >> .env

register-app:
	@if [ ! -f .env ]; then \
		echo "Error: .env file not found. Please run 'make deploy-outpost' and 'make deploy-app' first."; \
		exit 1; \
	fi; \
	set -a; \
	. $(PWD)/.env; \
	set +a; \
	if [ "$(verbose)" = "true" ]; then \
		result=$$(sui client call --package ${OUTPOST_ADDR} --module outpost --function register_app --args ${OUTPOST_APP_REGISTRY} ${APP_ADDR} ${APP_STATE} 1 sparsityxyz/abci-fib sha256:d10e26f90061400174e3f48f16da183c5ea2e2595c1fb050edfae1cdd4322f21 --json); \
		echo "$$result"; \
	else \
		result=$$(sui client call --package ${OUTPOST_ADDR} --module outpost --function register_app --args ${OUTPOST_APP_REGISTRY} ${APP_ADDR} ${APP_STATE} 1 sparsityxyz/abci-fib sha256:d10e26f90061400174e3f48f16da183c5ea2e2595c1fb050edfae1cdd4322f21 --json 2>/dev/null); \
	fi; \
	status=$$(echo "$$result" | jq -r '.effects.status.status'); \
	if [ "$$status" = "success" ]; then \
		echo "App registration successful!"; \
	else \
		echo "App registration failed!"; \
		if [ "$(verbose)" = "true" ]; then \
			echo "Error details:"; \
			echo "$$result" | jq '.'; \
		fi; \
		exit 1; \
	fi

approve-app:
	@if [ ! -f .env ]; then \
		echo "Error: .env file not found. Please run 'make deploy-outpost' and 'make deploy-app' first."; \
		exit 1; \
	fi; \
	set -a; \
	. $(PWD)/.env; \
	set +a; \
	if [ "$(verbose)" = "true" ]; then \
		result=$$(sui client call --package ${OUTPOST_ADDR} --module outpost --function approve_app --args ${OUTPOST_ADMIN_CAP} ${OUTPOST_APP_REGISTRY} ${APP_ADDR} --json); \
		echo "$$result"; \
	else \
		result=$$(sui client call --package ${OUTPOST_ADDR} --module outpost --function approve_app --args ${OUTPOST_ADMIN_CAP} ${OUTPOST_APP_REGISTRY} ${APP_ADDR} --json 2>/dev/null); \
	fi; \
	status=$$(echo "$$result" | jq -r '.effects.status.status'); \
	if [ "$$status" = "success" ]; then \
		echo "App approval successful!"; \
	else \
		echo "App approval failed!"; \
		if [ "$(verbose)" = "true" ]; then \
			echo "Error details:"; \
			echo "$$result" | jq '.'; \
		fi; \
		exit 1; \
	fi

new-session:
	@if [ ! -f .env ]; then \
		echo "Error: .env file not found. Please run 'make deploy-outpost' and 'make deploy-app' first."; \
		exit 1; \
	fi; \
	set -a; \
	. $(PWD)/.env; \
	set +a; \
	if [ "$(verbose)" = "true" ]; then \
		result=$$(sui client call --package ${APP_ADDR} --module app --function create_session --args ${OUTPOST_APP_REGISTRY} ${OUTPOST_APP_SESSION} ${APP_ADDR} ${APP_STATE} 11 --json); \
		echo "$$result"; \
	else \
		result=$$(sui client call --package ${APP_ADDR} --module app --function create_session --args ${OUTPOST_APP_REGISTRY} ${OUTPOST_APP_SESSION} ${APP_ADDR} ${APP_STATE} 11 --json 2>/dev/null); \
	fi; \
	status=$$(echo "$$result" | jq -r '.effects.status.status'); \
	if [ "$$status" = "success" ]; then \
		echo "Session creation successful!"; \
	else \
		echo "Session creation failed!"; \
		if [ "$(verbose)" = "true" ]; then \
			echo "Error details:"; \
			echo "$$result" | jq '.'; \
		fi; \
		exit 1; \
	fi

session-result:
	@if [ ! -f .env ]; then \
		echo "Error: .env file not found. Please run 'make deploy-outpost' and 'make deploy-app' first."; \
		exit 1; \
	fi; \
	set -a; \
	. $(PWD)/.env; \
	set +a; \
	if [ "$(verbose)" = "true" ]; then \
		result=$$(sui client call --package ${OUTPOST_ADDR} --module outpost --function get_session_info --args ${OUTPOST_APP_SESSION} ${APP_ADDR} 1 --dev-inspect --json); \
		echo "$$result"; \
	else \
		result=$$(sui client call --package ${OUTPOST_ADDR} --module outpost --function get_session_info --args ${OUTPOST_APP_SESSION} ${APP_ADDR} 1 --dev-inspect --json 2>/dev/null); \
	fi; \
	status=$$(echo "$$result" | jq -r '.effects.status.status'); \
	if [ "$$status" = "success" ]; then \
		echo "Session result check successful!"; \
	else \
		echo "Session result check failed!"; \
		if [ "$(verbose)" = "true" ]; then \
			echo "Error details:"; \
			echo "$$result" | jq '.'; \
		fi; \
		exit 1; \
	fi
 
