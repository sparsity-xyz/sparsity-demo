ifneq (,$(wildcard .env))
    include .env
    export
endif

node:
	pkill -f anvil || true
	nohup anvil > anvil.log 2>&1 &
	$(MAKE) deploy
	tail -f anvil.log

deploy:
	rm -rf ignition/deployments
	npx hardhat ignition deploy ignition/modules/APP.ts --network localhost
	npx hardhat ignition deploy ignition/modules/MockOutpost.ts --network localhost

request-fib:
	cast send ${APP_CONTRACT} --private-key ${DEPLOYER_PRIVATE_KEY} "requestFib(uint256)" ${NUM}
	@RAW_DATA=$$(cast call ${APP_CONTRACT} "initialData(uint256)" ${NUM}) && \
    cast abi-decode "initialData(uint256)(bytes)" "$$RAW_DATA"

settle-result:
	RESULT=${RESULT} NUM=${NUM} npx hardhat test test/app.ts --network localhost

base-sepolia-deploy:
	npx hardhat ignition deploy ignition/modules/APP.ts --network base_sepolia

base-sepolia-register:
	# register app to base_sepolia Sparsity outpost contract
	# wait for the owner approve our request
	cast send ${OUTPOST_PROXY_CONTRACT} --private-key ${DEPLOYER_PRIVATE_KEY} --rpc-url ${BASE_SEPOLIA_RPC} "registerAPP(address,string,string)" ${APP_CONTRACT} ${DOCKER_URI} ${DOCKER_HASH}

base-sepolia-sessionId:
	cast call ${APP_CONTRACT} --rpc-url ${BASE_SEPOLIA_RPC} "nextSessionId()"

base-sepolia-fib:
	# request fib number
	cast send ${APP_CONTRACT} --private-key ${DEPLOYER_PRIVATE_KEY} --rpc-url ${BASE_SEPOLIA_RPC} "requestFib(uint256)" 8

base-sepolia-fib-result:
	# check result
	cast call ${APP_CONTRACT} --rpc-url ${BASE_SEPOLIA_RPC} "getFibonacci(uint256)" 8
