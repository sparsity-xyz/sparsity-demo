# Sparsity TEE Demo

Guide to build your own local TEE-based off-chain computing workflow


## Install Foundry for local EVM node

You need to run a local EVM node to deploy contracts, and we will be using `anvil` which is provided with `foundry`. Run the following commands to install foundry and set it up on the terminal.
```
curl -L https://foundry.paradigm.xyz | bash
source ~/.bashrc
foundryup
```

## Pull & build relevant docker images
In terminal, go to the directory of **fibonacci-js-tee**
```
docker pull sparsityxyz/fleet:20250421141233
docker pull sparsityxyz/bridge:20250421142445


docker build -t nitro-parent:latest -f docker/Dockerfile.parent .

# sample application
docker build -t nitro-enclave-sim:latest -f docker/Dockerfile.enclave_sim .
```

 - The first two images are the bridge and fleet applications. Bridge will listen to new computing sessions requested from the APP contract on the Outpost contract and pass on new computing requests to Manager contract
 - Fleet will listen to manager contract for any new computing requests. If there is a new request, it will start docker containers to carry out the computation.
 - For more detailed information on the contracts, check `evm/README.md`
 - Once the computation is done, fleet will send transaction to the Outpost contract to submit the result.
 - In TEE, a single node will be sufficient to trigger settlement of the process, and the result should then be transferred over to the app contract to be used.

## Set up environemnt & environment variables

1. Under the **fibonacci-js-tee** directory, copy over the `.env.example` file to `.env` to set up basic environment variables for fleet and bridge.
   ```
   # From terminal of the directory of [fibonacci-js-tee]
   cp .env.example .env
   ```
2. Under `evm/`, copy over `.env.local.example` to `.env`.
   ```
   # From terminal of the directory of [fibonacci-js-tee]
   cd evm
   cp .env.local.example .env
   ```
3. Make any necessary changes in the `.env` file. (The only variable you should change is `DOCKER_URI`, which is the docker URI to your customized application) By default, you shouldn't need to change anything.
4. Under `evm/`, install hardhat using the following command
```
npm install hardhat
```

## Test Run to see everything works
1. Under `evm/` run the following code to start the EVM node and set up the contracts. 
```
make node
```

2. Open another terminal, under the **fibonacci-js-tee** directory, run the bridge container. Note the command difference in Linux and WSL & Mac
```
# For Linux
make bridge-start

# For WSL2 and Mac
make bridge-start-DHI
```

 > - This will start the bridge process to relay the events between manager and outpost contracts.

3. After the EVM node is done deploying contracts & sending out the tokens to the addresses, run the fleet container in another terminal under the **fibonacci-js-tee** directory.
```
# For Linux
make fleet-start

# For WSL2 and Mac
make fleet-start-DHI
```


 - Sample output when the node is finished setting up the environment:
```
[ NitroValidatorModule ] successfully deployed 🚀

Deployed Addresses

OutpostProxyModule#Outpost - 0x5FbDB2315678afecb367f032d93F642f64180aa3
OutpostProxyModule#TransparentUpgradeableProxy - 0xe7f1725E7734CE288F8367e1Bb143E90bb3F0512
OutpostProxyModule#ProxyAdmin - 0xCafac3dD18aC6c6e92c921884f9E4176737C052c
OutpostModule#Outpost - 0xe7f1725E7734CE288F8367e1Bb143E90bb3F0512
ManagerProxyModule#Manager - 0x9fE46736679d2D9a65F0992F2272dE9f3c7fa6e0
ManagerProxyModule#TransparentUpgradeableProxy - 0xCf7Ed3AccA5a467e9e704C703E8D87F634fB0Fc9
ManagerProxyModule#ProxyAdmin - 0xd8058efe0198ae9dD7D563e1b4938Dcbc86A1F81
ManagerModule#Manager - 0xCf7Ed3AccA5a467e9e704C703E8D87F634fB0Fc9
appModule#APP - 0xDc64a140Aa3E981100a9becA4E685f962f0cF6C9
certManagerModule#CertManager - 0x5FC8d32690cc91D4c39d9d3abcBD16989F875707
NitroValidatorModule#NitroValidator - 0x0165878A594ca255338adfa4d48449f69242Eb8F
```

 > - This will start listening events on the manager contract to see if there's any new computing reqeusts.
 > - If you have run fleet before and have .data directory in the base directory, you will have to remove it using the command `sudo rm -rf .data` before running `make start-fleet` to remove any leftover data from the previous run

4. in another terminal, go to `evm/` directory and make a new computation request using the command below
```
make request-fib NUM=20 EXEC_TYPE=1
```

 > - Expected output looks something like this:
 ```
     make request-fib NUM=20 EXEC_TYPE=1
[SPARSITY] Requesting new Fibonacci calculation session to execution type 1...
cast send 0xDc64a140Aa3E981100a9becA4E685f962f0cF6C9 --private-key 0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80 "requestFib(uint256,uint8)" 20 1

blockHash            0x6036d9c63f494fd0646898e976a4215ab0de640340647a7011fecc244b2678d5
blockNumber          83
contractAddress      
cumulativeGasUsed    110788
effectiveGasPrice    1000018454
from                 0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266
gasUsed              110788
logs                 ... (omitted)
root                 
status               1 (success)
transactionHash      0x11c10c64a1b1f0128253c008058be6cb33b5e593b156265900b622029d202f2a
transactionIndex     0
type                 2
blobGasPrice         1
blobGasUsed          
authorizationList    
to                   0xDc64a140Aa3E981100a9becA4E685f962f0cF6C9
 ```

5. wait for some time for the fleet to deploy & get the results back & settle on the EVM node.

 > - Expected output on fleet receiving a new computation request:
 ```
     fleet-run-1  | I[2025-04-21|09:27:30.732] New session log                              block=84 txHash=0xff992c7a64a4450ba0c50c62c8b3ead0d32124a51719e5a29694b95e8107cfe7 index=0
fleet-run-1  | Unpacked data: [
fleet-run-1  |   "0xDc64a140Aa3E981100a9becA4E685f962f0cF6C9",
fleet-run-1  |   [
fleet-run-1  |     {
fleet-run-1  |       "endpoint": "127.0.0.1:30000",
fleet-run-1  |       "pubKeyAddress": "0x3fcf1a0a658cbd89577dfb2559a99a68bd2b8c80",
fleet-run-1  |       "validatorPubKey": "Ajkk5/cwvDufhFNSRB5nxD2DxtS0lkNoRsKDiM+8+wGd",
fleet-run-1  |       "nodeId": "783be8ffe057803ecf671439f3c797410b768cd3@127.0.0.1:40000",
fleet-run-1  |       "dockerURI": "nitro-enclave-sim:latest",
fleet-run-1  |       "dockerHash": "sha256:d10e26f90061400174e3f48f16da183c5ea2e2595c1fb050edfae1cdd4322f21",
fleet-run-1  |       "initialData": "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABQ=",
fleet-run-1  |       "status": 0,
fleet-run-1  |       "execType": 1
fleet-run-1  |     }
fleet-run-1  |   ]
fleet-run-1  | ]
 ```
 > - during calculation & verification:
 ```
     leet-run-1  | I[2025-04-21|09:27:33.261] Receive settlement                           settlement="&{Name:ss-0x....(omitted)
     fleet-run-1  | I[2025-04-21|09:27:33.261] Start to send settlement                     data="&{Name:ss-0x....(omitted)
     fleet-run-1  | I[2025-04-21|09:27:34.269] Settlement sent succeed                      data="&{Name:ss-0x....(omitted)
 ```
 > - the settlement process includes attestation verification as well as result submission, which triggers the settlement.

6. Finally after those are done, you can check the result with the following command:
```
make get-fib NUM=20
[SPARSITY] Requesting new Fibonacci calculation session...
6765
```

## Implement your customized application

1. Edit `evm/contracts/APP.sol` for on-chain contract customization. This is the part where you modify application contract logic for new computation session creation & initial data management.

2. The `INIT_DATA` passed onto the APP.sol contract will be transferred over to simple_enclave_app.py for app initialization.

2. Edit `apps/simple_enclave_app.py` for off-chain computation logic. Make sure you update `self.result` for the enclave app so the fleet process can read in the final result to be submitted to the outpost contract.


4. Once you edit  `apps/simple_enclave_app.py` you can update the image used in the fleet by re-building the enclave simulation image with the following command
```
 docker build -t nitro-enclave-sim:latest -f docker/Dockerfile.enclave_sim .
```

5. After building the image, you can re-do the process above to test your application. When you re-run fleet, make sure you delete any data left over from the last run by deleting .data in the base directory.
```
 rm -r .data
```
