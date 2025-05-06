RED=\033[0;31m
GREEN=\033[0;32m
NC=\033[0m # No Color

ifneq (,$(wildcard .env))
    include .env
    export
endif

OS := $(shell uname -s)
ifeq ($(OS),Linux)
    KILL_ANVIL = -pkill -f anvil
else
    KILL_ANVIL = pkill -f anvil || true
endif

PID_FILE := process.pid

.PHONY: node deploy test-proxy send-settle-eth new-session authin authout session-result fib-result register-app approve-app approver upgrade-outpost er clear

node:
	$(KILL_ANVIL)
	nohup anvil --block-time 1 --silent > nohup.log 2>&1 &
	@echo "INFO: Local node started, block time is 1s"
	@echo "$(GREEN)INFO: Deploying contracts$(NC)"
	${MAKE} deploy
	@echo "$(GREEN)INFO: All of the outpost/manager/app contracts deployed$(NC)"
	${MAKE} send-settle-eth
	@echo "$(GREEN)INFO: Send transaction to register app to the outpost$(NC)"
	${MAKE} register-app
	@echo "$(GREEN)INFO: Transaction succeed, app registered$(NC)"
	@echo ""
	@echo "$(GREEN)INFO: Send transaction to outpost to approve app$(NC)"
	${MAKE} approve-app
	@echo "$(GREEN)INFO: Transaction succeed, app approved$(NC)"
	@echo ""
	@echo "$(GREEN)INFO: Send transaction to set bridge addresses$(NC)"
	${MAKE} set-manager-bridge
	${MAKE} set-outpost-bridge
	@echo "$(GREEN)INFO: Bridge addresses set$(NC)"
	@echo "$(GREEN)INFO: Initialization complete$(NC)"
	@tail -f nohup.log

deploy:
	npx hardhat ignition deploy ignition/modules/OutpostProxy.ts --network localhost
	@echo "$(GREEN)INFO: Outpost contract deployed$(NC)"
	npx hardhat ignition deploy ignition/modules/ManagerProxy.ts --network localhost
	@echo "$(GREEN)INFO: Manager contract deployed$(NC)"
	npx hardhat ignition deploy ignition/modules/APP.ts --network localhost
	@echo "$(GREEN)INFO: APP contract deployed$(NC)"

send-settle-eth:
	cast send ${FLEET_SETTLER_ADDRESS} --value 10ether --private-key ${PROXY_ADMIN_PRIVATE_KEY}
	cast balance ${FLEET_SETTLER_ADDRESS}


## app
request-fib:
	cast send ${APP_CONTRACT} --private-key ${PROXY_ADMIN_PRIVATE_KEY} "requestFib(uint256)" ${NUM}

fib-result:
	@cast abi-decode "getFibonacci(uint256)(uint256)" $(shell cast call ${APP_CONTRACT} --private-key ${CONTRACT_OWNER_PRIVATE_KEY} "getFibonacci(uint256)" ${NUM})	

register-app:
	cast send ${OUTPOST_PROXY_CONTRACT} --private-key ${PROXY_ADMIN_PRIVATE_KEY} "registerAPP(address,string,string)" ${APP_CONTRACT} ${APP_NAME} ${DOCKER_URI} ${DOCKER_HASH}

## sparsity
approve-app:
	cast send ${OUTPOST_PROXY_CONTRACT} --private-key ${CONTRACT_OWNER_PRIVATE_KEY} "approveAPP(address)" ${APP_CONTRACT}

set-outpost-bridge:
	cast send ${OUTPOST_PROXY_CONTRACT} --private-key ${CONTRACT_OWNER_PRIVATE_KEY} "setBridge(address,bool)" 0x3C44CdDdB6a900fa2b585dd299e03d12FA4293BC true

set-manager-bridge:
	cast send ${MANAGER_PROXY_CONTRACT} --private-key ${CONTRACT_OWNER_PRIVATE_KEY} "setBridge(address,bool)" 0x90F79bf6EB2c4f870365E785982E1f101E93b906 true
