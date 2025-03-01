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

join:
	cast send ${APP_CONTRACT} --private-key ${DEPLOYER_PRIVATE_KEY} "joinOrCreateRoom()"

join2:
	cast send ${APP_CONTRACT} --private-key ${DEPLOYER_PRIVATE_KEY} "joinOrCreateRoom()"

session:
	@RAW_DATA=$$(cast call ${APP_CONTRACT} "getSession()" ${SID}) && \
    cast abi-decode "getSession()((string,address,uint8))" "$$RAW_DATA"

callback-session:
	cast send ${OUTPOST_PROXY_CONTRACT} --private-key ${DEPLOYER_PRIVATE_KEY} "callbackSession(address,uint256,(string,address,uint8))" ${APP_CONTRACT} ${SID} '("http://127.0.0.1:9981", ${APP_CONTRACT}, 2)'

callback-settle:
	cast send ${OUTPOST_PROXY_CONTRACT} --private-key ${DEPLOYER_PRIVATE_KEY} "settle(address,uint256,bool,bytes)" ${APP_CONTRACT} ${SID} false ${RESULT}

room:
	cast call ${APP_CONTRACT} "getRoom(uint256)" 1
