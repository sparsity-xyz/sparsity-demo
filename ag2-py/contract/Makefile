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
	sleep 1
	${MAKE} deploy
	${MAKE} test-proxy
	${MAKE} send-settle-eth
	${MAKE} register-app
	${MAKE} approve-app
	${MAKE} set-manager-bridge
	${MAKE} set-outpost-bridge
	${MAKE} test-event
	tail -f nohup.log

deploy:
	npx hardhat ignition deploy ignition/modules/OutpostProxy.ts --network localhost
	npx hardhat ignition deploy ignition/modules/ManagerProxy.ts --network localhost
	npx hardhat ignition deploy ignition/modules/APP.ts --network localhost
	# after deployment, move the abi file to the bridge
	cp ignition/deployments/chain-31337/artifacts/OutpostProxyModule#Outpost.json ../bridge/src/abi/Outpost.json
	cp ignition/deployments/chain-31337/artifacts/ManagerProxyModule#Manager.json ../bridge/src/abi/Manager.json

test-proxy:
	npx hardhat test test/Proxy.ts --network localhost

test-event:
	npx hardhat test test/Event.ts --network localhost

send-settle-eth:
	cast send ${FLEET_SETTLER_ADDRESS} --value 10ether --private-key ${PROXY_ADMIN_PRIVATE_KEY}
	cast balance ${FLEET_SETTLER_ADDRESS}


## app
new-session:
	cast send ${APP_CONTRACT} --private-key ${PROXY_ADMIN_PRIVATE_KEY} "requestFib(uint256)" 11

authin:
	cast send ${APP_CONTRACT} --private-key ${PROXY_ADMIN_PRIVATE_KEY} "authIn(uint256)" 0

authout:
	cast send ${APP_CONTRACT} --private-key ${PROXY_ADMIN_PRIVATE_KEY} "authOut(uint256)" 0

session-result:
	@cast abi-decode "_sessions(uint256)(string,address,uint)" $(shell cast call ${APP_CONTRACT} --private-key ${CONTRACT_OWNER_PRIVATE_KEY} "_sessions(uint256)" 0)

fib-result:
	@cast abi-decode "getFibonacci(uint256)(uint256)" $(shell cast call ${APP_CONTRACT} --private-key ${CONTRACT_OWNER_PRIVATE_KEY} "getFibonacci(uint256)" 11)	

## outpost
register-app:
	cast send ${OUTPOST_PROXY_CONTRACT} --private-key ${PROXY_ADMIN_PRIVATE_KEY} "registerAPP(address,string,string)" ${APP_CONTRACT} ${APP_NAME} ${DOCKER_URI} ${DOCKER_HASH}

approve-app:
	cast send ${OUTPOST_PROXY_CONTRACT} --private-key ${CONTRACT_OWNER_PRIVATE_KEY} "approveAPP(address)" ${APP_CONTRACT}

approver:
	cast call ${OUTPOST_PROXY_CONTRACT} "_approver(address)" ${CONTRACT_OWNER_ADDRESS}

approval:
	cast call ${OUTPOST_PROXY_CONTRACT} "_appApproval(address)" ${APP_CONTRACT}

upgrade-outpost:
	npx hardhat ignition deploy ignition/modules/OutpostUpgrade.ts

set-outpost-bridge:
	cast send ${OUTPOST_PROXY_CONTRACT} --private-key ${CONTRACT_OWNER_PRIVATE_KEY} "setBridge(address,bool)" 0x3C44CdDdB6a900fa2b585dd299e03d12FA4293BC true

## manager
er:
	cast call ${MANAGER_PROXY_CONTRACT} --private-key ${CONTRACT_OWNER_PRIVATE_KEY} "availableER()"

clear:
	cast send ${MANAGER_PROXY_CONTRACT} --private-key ${CONTRACT_OWNER_PRIVATE_KEY} "clear()"

set-manager-bridge:
	cast send ${MANAGER_PROXY_CONTRACT} --private-key ${CONTRACT_OWNER_PRIVATE_KEY} "setBridge(address,bool)" 0x90F79bf6EB2c4f870365E785982E1f101E93b906 true
