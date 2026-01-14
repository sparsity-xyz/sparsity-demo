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
	nohup anvil --block-time 1 > nohup.log 2>&1 &
	${MAKE} deploy
	${MAKE} send-settle-eth
	${MAKE} register-app
	${MAKE} approve-app
	${MAKE} set-manager-bridge
	${MAKE} set-outpost-bridge
	tail -f nohup.log

deploy:
	npx hardhat ignition deploy ignition/modules/OutpostProxy.ts --network localhost
	npx hardhat ignition deploy ignition/modules/ManagerProxy.ts --network localhost
	npx hardhat ignition deploy ignition/modules/APP.ts --network localhost

send-settle-eth:
	cast send ${FLEET_SETTLER_ADDRESS} --value 10ether --private-key ${PROXY_ADMIN_PRIVATE_KEY}
	cast balance ${FLEET_SETTLER_ADDRESS}


## app
register-app:
	cast send ${OUTPOST_PROXY_CONTRACT} --private-key ${PROXY_ADMIN_PRIVATE_KEY} "registerAPP(address,uint,string,string)" ${APP_CONTRACT} 2 ${DOCKER_URI} ${DOCKER_HASH}


## sparsity
approve-app:
	cast send ${OUTPOST_PROXY_CONTRACT} --private-key ${CONTRACT_OWNER_PRIVATE_KEY} "approveAPP(address)" ${APP_CONTRACT}

set-outpost-bridge:
	cast send ${OUTPOST_PROXY_CONTRACT} --private-key ${CONTRACT_OWNER_PRIVATE_KEY} "setBridge(address,bool)" 0x3C44CdDdB6a900fa2b585dd299e03d12FA4293BC true

set-manager-bridge:
	cast send ${MANAGER_PROXY_CONTRACT} --private-key ${CONTRACT_OWNER_PRIVATE_KEY} "setBridge(uint256,address,bool)" $(shell cast chain-id) 0x90F79bf6EB2c4f870365E785982E1f101E93b906 true
