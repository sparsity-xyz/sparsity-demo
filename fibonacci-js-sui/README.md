# Fibonacci  

This demo showcases interaction with the **Sparsity Platform**. The application computes the Fibonacci sequence, allowing users to submit requests via a smart contract. The contract forwards these requests to the Sparsity platform, which processes them using the **App ABCI core** and returns the results back to the smart contract.

The Fibonacci sequence is computed recursively in this demo, which makes it an intensive computation. This type of recursive calculation is not feasible to perform on-chain due to its resource requirements, but it serves as an excellent example of the computational power of Sparsity. By offloading this computation to Sparsity, we demonstrate the platform's ability to handle complex and resource-heavy tasks efficiently.
 
---

## Running the App Locally  

### Prerequisites  
- **OS:** macOS or Linux (Windows users should use WSL)
- **Dependencies:**  
  - [Foundry](https://book.getfoundry.sh/): Ethereum development toolchain for smart contract development. This is used for manager contract simulation.
  - [Sui CLI](https://docs.sui.io/guides/developer/getting-started/sui-install). This is for outpost and app contracts simulation. 
    ```bash
    curl -L https://foundry.paradigm.xyz | bash
    foundryup
    ```
  - Node.js package manager: Install either [npm](https://nodejs.org/) (comes with Node.js) or [yarn](https://yarnpkg.com/getting-started/install)
  - **Docker**: Container platform for running services
    - [Install Docker for Mac](https://docs.docker.com/desktop/install/mac-install/)
    - [Install Docker for Linux](https://docs.docker.com/engine/install/)
    - [Install Docker for Windows + WSL](https://docs.docker.com/desktop/windows/wsl/)
  - *jq* cmd tool (https://jqlang.org/)
  
Make sure all services are properly installed and Docker daemon is running before proceeding with the setup.

### Project Structure
```
.
├── README.md                           # Project documentation

├── contract                            # Smart contract-related files
│   ├── manager                         # Ethereum manager contract
│   │   ├── Makefile                    # Build automation script
│   │   ├── Makefile_sepolia            # Build script for Sepolia testnet
│   │   ├── contracts                   # Solidity smart contracts
│   │   │   ├── Manager.sol             # Contract for managing fleets
│   │   │   ├── Proxy.sol               # Proxy contract for upgradeability
│   │   │   └── util.sol                # Utility functions for contracts
│   │   ├── hardhat.config.ts           # Hardhat configuration for Ethereum development
│   │   ├── package.json                # Dependencies and scripts for contract development
│   │   └── tsconfig.json               # TypeScript configuration for contract project
│   └── outpost                         # Sui outpost and app contracts
│       ├── outpost                     # Sui outpost contract
│       │   ├── sources                 # Move source files
│       │   │   └── outpost.move        # Main outpost contract implementation
│       │   ├── tests                   # Test files
│       │   ├── Move.toml               # Move package configuration
│       │   └── Move.lock               # Move dependency lock file
│       ├── app                         # Sui app contract
│       │   ├── sources                 # Move source files
│       │   │   └── app.move            # Main app contract implementation
│       │   ├── tests                   # Test files
│       │   ├── Move.toml               # Move package configuration
│       │   └── Move.lock               # Move dependency lock file
│       ├── README.md                   # Outpost documentation
│       ├── README_WIN_INSTALL.md       # Windows installation guide
│       └── Makefile                    # Build automation for outpost

└── server                              # Backend server code
    ├── Dockerfile                      # Docker configuration for containerization
    ├── Makefile                        # Build automation for the ABCI
    ├── package.json                    # Dependencies and scripts for the backend
    ├── src                             # Source code for the ABCI core
    │   └── index.ts                    # Entry point for the ABCI core
    └── tsconfig.json                   # TypeScript configuration for the ABCI core

```

### 1. Build the Docker Image  
The Docker image contains the ABCI core, encapsulating all computation and execution logic.  

Open a new terminal in the **fibonacci-js-sui** directory:  
```bash
cd server
docker build -t abci-fib-sui:latest .
```  

### 2. Start the manager Chain Node (EVM) and Deploy the manager Smart Contract  
This step simulates an EVM chain locally and deploys the smart contract.  

Open a new terminal in the **fibonacci-js-sui** directory:  
```bash
cd contract/manager

# Ignore any warning messages
npm install 

# Pre-configured example environment variables for quick setup.
# Please avoid committing sensitive credentials to Git.
cp .env.example .env

make node
```  

Wait until blocks start building before proceeding. Check the terminal output to ensure blocks are being produced.

Once you see a consistent block mining signal in the terminal, as shown in the example below, you can proceed to the next section.

```
    Block Number: 36
    Block Hash: 0xf883b971d3024ebb9c2391eef0478a0b587ec3a58b1837b5a297b8028daaf116  
    Block Time: "Wed, 19 Mar 2025 23:07:42 +0000"  

    Block Number: 37  
    Block Hash: 0x973de0985c3e0aee02a8f2e78eb9d3301cfdda83812077bbbf27dc9bcc6df47e  
    Block Time: "Wed, 19 Mar 2025 23:07:43 +0000"  
```  

### 3. Start the outpost and app chain node (Sui) and deploy outpost and app contract

Open one terminal, start Sui local node
```
cd contract/outpost
make node
```

Open another terminal, deploy the outpost contract
```
cd contract/outpost

make faucet

make deploy-outpost

```
You should see something like this
```
Outpost Contract Deployed. Environment Variables:
OUTPOST_ADDR=0x7229006c4b321b944510650d845a01bdeb4faf4fae1dec4b69f884c484cdad4a
OUTPOST_ADMIN_CAP=0x020dd6110d6d1f9cf3c0741dcb088e729632c9fb3f19f3c588e6cfa3fc72bb82
OUTPOST_APP_REGISTRY=0x6de6062b95f79935da89c30432b1bad124ea81e963ebe535ac63ef2d5b0af984
OUTPOST_APP_SESSION=0xb22201440712fab15547b19b84260b05822560dd507989ec4aab3fe1c12de22c
```

Take the value of [OUTPOST_ADDR], fill that in sparsity address in fibonacci-js-sui\contract\outpost\app\Move.toml, like
```
[addresses]
sparsity = "0x7229006c4b321b944510650d845a01bdeb4faf4fae1dec4b69f884c484cdad4a" 
app = "0x0"
```

Then deploy app address
```
make deploy-app
```

You would see 
```
App Contract Deployed. Environment Variables:
APP_ADDR=0xb6c34eef8b42bb603249642c5374ede4731602781188f7df293a6950643c615c
APP_STATE=0x8b808063cc1851159f7b319d3c1d88a8c59b25a091b25a585f1fd0168959d5bc
```

Then register app and approve app
```
make register-app

make approve-app
```


### 4. Start the Bridge  
The **Bridge** service connects the host EVM chain with the **Sparsity platform**.  

Update [OutpostAddress] in `bridge/.env.example` with the value of [OUTPOST_ADDR], for example
```
OutpostAddress=0x7229006c4b321b944510650d845a01bdeb4faf4fae1dec4b69f884c484cdad4a
```

Open a new terminal and run:  
```bash
docker pull sparsityxyz/bridge:20250420230231 
 
# macOS and wsl
docker run --rm -ti --env-file bridge/.env.example -e HOST=host.docker.internal sparsityxyz/bridge:20250420230231  

# Linux
docker run --rm -ti --env-file bridge/.env.example -e HOST=172.17.0.1 sparsityxyz/bridge:20250420230231 
```  



Once you see the following signal in the terminal, it indicates that the bridge service has started and is running. You can now proceed to the next section.  

```
Sui-Event-Query request: ...
```  


### 5. Start the Fleet  
The **Fleet** service triggers the Sparsity execution session upon receiving signals from the host chain via the Bridge service.  

Open a new terminal and pull the Fleet images:  
```bash
docker pull sparsityxyz/fleet:20250422005123
docker pull sparsityxyz/fleet-er:latest
```  

Then, run the Fleet service:  

```bash
# macOS and wsl
docker run -ti --rm \
    --env-file fleet/.env.example \
    -v /var/run/docker.sock:/var/run/docker.sock \
    sparsityxyz/fleet:20250422005123 fleet run --local

# Linux 
docker run -ti --rm \
    --env-file fleet/.env.example \
    -v /var/run/docker.sock:/var/run/docker.sock \
    --add-host=host.docker.internal:172.17.0.1 \
    sparsityxyz/fleet:20250422005123 fleet run --local
```  

Once the following signal appears in the terminal, it confirms that the fleet service has successfully started and is running. You can now proceed to the next section.  

```
I[2025-03-19|23:19:33.317] All historical data processed                module=eventListener 
```  

### 6. Interact with the Smart Contract  
Once everything is running locally, you can perform end-to-end testing by interacting with the smart contract.  

To compute Fibonacci for a given number (e.g., `30`, the parameter is in `new-session` cmd in the Makefile):  

Open a new terminal in the **fibonacci-js-sui** directory:  
```bash
cd contract/outpost
make new-session
```   

Wait for the **Bridge** and **Fleet** to process the request. The system will first start the ABCI container and then compute the result, each taking several seconds depending on the machine's performance. Once you see a message like this in the Fleet terminal:

```
I[2025-04-22|08:10:27.694] Settlement sent succeed 
```

It indicates that the settlement was successful. Then, retrieve the result by running:  

```bash
make session-result
```  

**Expected output:**  

```bash
Session result check successful!
Contract vector data: [
  6,
  56,
  51,
  50,
  48,
  52,
  48
]
Converted data: 832040
```  

---
