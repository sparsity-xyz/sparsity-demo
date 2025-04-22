# Load environment variables from .env file if it exists
ifneq (,$(wildcard .env))
    include .env
    export
endif

# Determine OS for anvil process management
OS := $(shell uname -s)
ifeq ($(OS),Linux)
    KILL_ANVIL = -pkill -f anvil
else
    KILL_ANVIL = pkill -f anvil || true
endif

PID_FILE := process.pid

# Define log prefix for our commands
LOG_PREFIX := "[SPARSITY]"

# Default attestation URL for nitro enclave testing
ATTESTATION_URL ?= http://43.201.52.244:8001/attest

.PHONY: node deploy test-proxy send-settle-eth new-session authin authout session-result fib-result register-app approve-app approver upgrade-outpost er clear node-tee register-app-tee deploy-tee abi-tee

node:
	@echo "$(LOG_PREFIX) Starting local development environment..."
	$(KILL_ANVIL)
	nohup anvil --host 0.0.0.0 --block-time 1 --block-gas-limit 120000000 > nohup.log 2>&1 &
	sleep 1
	${MAKE} deploy
	${MAKE} register-validator
	${MAKE} test-proxy
	${MAKE} send-settle-eth
	${MAKE} set-manager-bridge
	${MAKE} set-outpost-bridge
	@echo "$(LOG_PREFIX) Local environment setup complete. Watching logs..."
	tail -f nohup.log

deploy:
	@echo "$(LOG_PREFIX) Deploying OutpostProxy..."
	npx hardhat ignition deploy ignition/modules/OutpostProxy.ts --network localhost
	@echo "$(LOG_PREFIX) Deploying ManagerProxy..."
	npx hardhat ignition deploy ignition/modules/ManagerProxy.ts --network localhost
	@echo "$(LOG_PREFIX) Deploying APP..."
	npx hardhat ignition deploy ignition/modules/APP.ts --network localhost
	@echo "$(LOG_PREFIX) Deploying Cert Manager..."
	npx hardhat ignition deploy ignition/modules/CertManager.ts --network localhost
	@echo "$(LOG_PREFIX) Deploying Nitro Validator..."
	npx hardhat ignition deploy ignition/modules/NitroValidator.ts --network localhost

abi:
	@echo "$(LOG_PREFIX) Copying ABI files to fleet service..."
	cp ignition/deployments/chain-31337/artifacts/OutpostProxyModule#Outpost.json ../../fleet/fleet/contract/Outpost.json
	cp ignition/deployments/chain-31337/artifacts/ManagerProxyModule#Manager.json ../../fleet/fleet/contract/Manager.json
	@echo "$(LOG_PREFIX) ABI files copied successfully"

test-proxy:
	@echo "$(LOG_PREFIX) Running proxy tests..."
	npx hardhat test test/Proxy.ts --network localhost

test-event:
	@echo "$(LOG_PREFIX) Running event tests..."
	npx hardhat test test/Event.ts --network localhost

send-settle-eth:
	@echo "$(LOG_PREFIX) Sending ETH to fleet settler..."
	cast send ${FLEET_SETTLER_ADDRESS} --value 10ether --private-key ${PROXY_ADMIN_PRIVATE_KEY}
	@echo "$(LOG_PREFIX) Checking fleet settler balance..."
	cast balance ${FLEET_SETTLER_ADDRESS}


## outpost 
approver:
	@echo "$(LOG_PREFIX) Checking if address is an approver..."
	cast call ${OUTPOST_PROXY_CONTRACT} "_approver(address)" ${CONTRACT_OWNER_ADDRESS}

approval:
	@echo "$(LOG_PREFIX) Checking if APP is approved..."
	cast call ${OUTPOST_PROXY_CONTRACT} "_appApproval(address)" ${APP_CONTRACT}

upgrade-outpost:
	@echo "$(LOG_PREFIX) Upgrading Outpost contract..."
	npx hardhat ignition deploy ignition/modules/OutpostUpgrade.ts

set-outpost-bridge:
	@echo "$(LOG_PREFIX) Setting bridge address for Outpost..."
	cast send ${OUTPOST_PROXY_CONTRACT} --private-key ${CONTRACT_OWNER_PRIVATE_KEY} "setBridge(address,bool)" 0x3C44CdDdB6a900fa2b585dd299e03d12FA4293BC true

set-approval-check:
	@echo "$(LOG_PREFIX) Setting APP approval check..."
	cast send ${OUTPOST_PROXY_CONTRACT} --private-key ${CONTRACT_OWNER_PRIVATE_KEY} "setApproveCheck(bool)" true

## manager
er:
	@echo "$(LOG_PREFIX) Checking available ER count..."
	cast call ${MANAGER_PROXY_CONTRACT} --private-key ${CONTRACT_OWNER_PRIVATE_KEY} "availableER()"

clear:
	@echo "$(LOG_PREFIX) Clearing all ER sessions..."
	cast send ${MANAGER_PROXY_CONTRACT} --private-key ${CONTRACT_OWNER_PRIVATE_KEY} "clear()"

set-manager-bridge:
	@echo "$(LOG_PREFIX) Setting bridge address for Manager..."
	cast send ${MANAGER_PROXY_CONTRACT} --private-key ${CONTRACT_OWNER_PRIVATE_KEY} "setBridge(address,bool)" 0x90F79bf6EB2c4f870365E785982E1f101E93b906 true

## TEE

register-validator:
	@echo "$(LOG_PREFIX) Registering Nitro Validator with TEE Outpost..."
	cast send ${OUTPOST_PROXY_CONTRACT} --private-key ${CONTRACT_OWNER_PRIVATE_KEY} "registerNitroValidator(address)" ${VALIDATOR_CONTRACT}

unregister-validator:
	@echo "$(LOG_PREFIX) Unregistering Nitro Validator from TEE Outpost..."
	cast send ${OUTPOST_PROXY_CONTRACT} --private-key ${CONTRACT_OWNER_PRIVATE_KEY} "unregisterNitroValidator()"

get-attestation:
	. ../../.venv/bin/activate && python3 scripts/decode_attestation.py ${ATTESTATION_URL}

decode_and_validate_attestation: get-attestation
	cast call ${OUTPOST_PROXY_CONTRACT} "decodeAndValidateAttestation(bytes)" $(shell cat attestation_hex.txt)

verify-signature:
	@echo "$(LOG_PREFIX) Verifying signature..."
	cast call ${OUTPOST_PROXY_CONTRACT} "verifySignatureTest(bytes,bytes,bytes)" $(shell cat result.txt) $(shell cat signature.txt) $(shell cat attestation_hex.txt)

