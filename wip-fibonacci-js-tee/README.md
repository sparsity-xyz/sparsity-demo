# Sparsity TEE Demo

Guide to build your own local TEE-based off-chain computing workflow

## Pull & build relevant docker images
 ```
 docker pull sparsityxyz/fleet:20250421141233

 docker pull sparsityxyz/bridge:20250421142445

 docker build -t nitro-parent:latest -f docker/Dockerfile.parent .

 # sample application
 docker build -t nitro-enclave-sim:latest -f docker/Dockerfile.enclave_sim
 ```

## Set up environemnt & environment variables

1. Under `evm/`, Copy over `.env.local.example` to `.env`.
2. Make any necessary changes in the `.env` file. (The only variable you should change is `DOCKER_URI`, which is the docker URI to your customized application)
3. Under `evm/`, install hardhat using the following command
```
npm install hardhat
```

## Test Run to see everything works
1. Under `evm/` run `make node` to start the EVM node and set up the contracts. If you customized `APP.sol`, you might want to check the address is deployed in the correct address in `.env`
```
## app
APP_CONTRACT=0xDc64a140Aa3E981100a9becA4E685f962f0cF6C9
```
2. In another terminal, run the bridge container
```
make start-bridge
```

3. After the node is done deploying contracts & sending out the tokens to the addresses, run the fleet container in another terminal.
```
make start-fleet
```

Sample output when the node is finished setting up the environment:
```
    Proxy interaction
manager 0xCf7Ed3AccA5a467e9e704C703E8D87F634fB0Fc9
BridgeStatusChanged Signature: 
...
Settle Signature: 0x25630e65672133ef8cb6e65a6590e1b6758b74ee8e3db00433012e9df8ac1a23
      ✔ Output


  2 passing (107ms)

make[1]: Leaving directory '/home/yl/Desktop/work/demo-sparsity/wip-fibonacci-js-tee/evm'
[SPARSITY] Local environment setup complete. Watching logs...

```
4. in another terminal, go to `evm/` directory and make a new computation request using the command below
```
make request-fib NUM=20 EXEC_TYPE=1
```

5. wait for some time for the fleet to deploy & get the results back & settle on the EVM node. Then, you can check the result with the following command:
```
make get-fib NUM=20
[SPARSITY] Requesting new Fibonacci calculation session...
6765
```

## Implement your customized application

1. Edit `evm/contracts/APP.sol` for on-chain contract customization
2. Edit `apps/simple_enclave_app.py` for off-chain computation logic.
3. The `INIT_DATA` passed onto the APP.sol contract will then be transferred over to simple_enclave_app.py for app initialization