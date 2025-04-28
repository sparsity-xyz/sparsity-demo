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
cp .env.local.example .env

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

#### Prerequisites
- **Install Sui CLI**
  - Follow the [official installation guide](https://docs.sui.io/guides/developer/getting-started/sui-install)

- **Configure Local Environment**
  - Follow the [Sui Client Configuration Guide](https://docs.sui.io/guides/developer/getting-started/connect#configure-sui-client)
  - Run the following command to start the configuration:
  ```bash
  sui client
  ```
  - When prompted, follow these steps:
    ```
    Config file ["~/.sui/sui_config/client.yaml"] doesn't exist, do you want to connect to a Sui Full node server [y/N]? y
    Sui Full node server URL (Defaults to Sui Testnet if not specified): 127.0.0.1:9000
    Environment alias for [127.0.0.1:9000]: local
    Select key scheme to generate keypair (0 for ed25519, 1 for secp256k1, 2: for secp256r1): 0
    ```
  - After configuration, you'll see:
    ```
    Generated new keypair and alias for address with scheme "ed25519" [competent-agates: 0x...]
    Secret Recovery Phrase: [mnemonic...]
    ```

  > **Important**: Save your Secret Recovery Phrase securely. You'll need it later for the fleet setup configuration.

#### Start Sui Local Node
Open one terminal, go to **fibonacci-js-sui** directory, start Sui local node
```
cd contract/outpost
make node
```

Open another terminal, go to **fibonacci-js-sui** directory, deploy the outpost contract
```
cd contract/outpost

make all
```

You should see something like this
```
...
Outpost Contract Deployed. Environment Variables:
OUTPOST_ADDR=0x6bc0a901f4f96490a9707eda598a2f584975bccdf24d220a9713aff2173bf6a9
OUTPOST_ADMIN_CAP=0x1401f8932c759258ab23e03dc500d54ae5bb8d33fe21c2905b7cbb03d5026a6c
OUTPOST_APP_REGISTRY=0xd23d11e3f312f39753938a5499f7d6af3c4085f46cf909500344c28b85938018
OUTPOST_APP_SESSION=0x086652cc580dc349d9046dcc6dda42d7e2bc2c65e1ae68460aa91ed57d7c37a4
...
App Contract Deployed. Environment Variables:
APP_ADDR=0x0981bba6ea5caac25c93240c14f236439e1314c7e92d38ed1c78e4b5cf9c7ff2
APP_STATE=0x4682c664a0758b6a6b71fae325f993d2fd8b1e737c11ec74701c73a79832797c
```
What happens behind this `make all` cmd:
it will faucet, deploy outpost contract, update app config and deploy app contract, register app and approve the app in outpost. For more details, please check the cmd in `fibonacci-js-sui\contract\outpost\Makefile`.


### 4. Start the Bridge  
The **Bridge** service connects the host EVM chain with the **Sparsity platform**.  

Update [OutpostAddress] in `bridge/.env.example` with the value of [OUTPOST_ADDR], for example
```
OutpostAddress=0x6bc0a901f4f96490a9707eda598a2f584975bccdf24d220a9713aff2173bf6a9
```

Open a new terminal, go to **fibonacci-js-sui** directory:  
```bash
docker pull sparsityxyz/bridge:20250427183346 
 
# macOS and wsl
docker run --rm -ti --env-file bridge/.env.example -e HOST=host.docker.internal sparsityxyz/bridge:20250427183346  

# Linux
docker run --rm -ti --env-file bridge/.env.example -e HOST=172.17.0.1 --add-host=host.docker.internal:host-gateway sparsityxyz/bridge:20250427183346 
```  



Once you see the following signal in the terminal, it indicates that the bridge service has started and is running. You can now proceed to the next section.  

```
Sui-Event-Query request: ...
```  


### 5. Start the Fleet  
The **Fleet** service triggers the Sparsity execution session upon receiving signals from the host chain via the Bridge service.  

Update envs in `fleet/.env.example` with the value of [OUTPOST_ADDR], [OUTPOST_APP_SESSION], [OUTPOST_ADMIN_CAP] as in step 3 above and update the mnemonic with your local admin account when setting up local Sui network, for example
```
SUI_OUTPOST_ADDRESS=0x6bc0a901f4f96490a9707eda598a2f584975bccdf24d220a9713aff2173bf6a9
SUI_OUTPOST_SESSION_ADDRESS=0x086652cc580dc349d9046dcc6dda42d7e2bc2c65e1ae68460aa91ed57d7c37a4
SUI_OUTPOST_ADMIN_CAP_ADDRESS=0x1401f8932c759258ab23e03dc500d54ae5bb8d33fe21c2905b7cbb03d5026a6c
SUI_OUTPOST_OWNER_MNEMONIC="reveal fold artefact hub unlock emotion seat harsh pelican tone upon mutual"
```



Open a new terminal, go to **fibonacci-js-sui** directory, pull the Fleet images:  
```bash
docker pull sparsityxyz/fleet:20250427174344
docker pull sparsityxyz/fleet-er:20250427174235
```  

Then, run the Fleet service:  

```bash
# macOS and wsl
docker run -ti --rm \
    -v ~/sparsity/fleet/data:/.data \
    --env-file fleet/.env.example \
    -v /var/run/docker.sock:/var/run/docker.sock \
    sparsityxyz/fleet:20250427174344 fleet run --local

# Linux 
docker run -ti --rm \
    -v ~/sparsity/fleet/data:/.data \
    -e HOST=172.17.0.1 \
    --env-file fleet/.env.example \
    -v /var/run/docker.sock:/var/run/docker.sock \
    --add-host=host.docker.internal:host-gateway \
    sparsityxyz/fleet:20250427174344 fleet run --local
```  

Once the following signal appears in the terminal, it confirms that the fleet service has successfully started and is running. You can now proceed to the next section.  

```
I[2025-03-19|23:19:33.317] All historical data processed                module=eventListener 
```  

### 6. Interact with the Smart Contract  
Once everything is running locally, you can perform end-to-end testing by interacting with the smart contract.  

To compute Fibonacci for a given number (e.g., `30`, the parameter is set in `new-session` cmd in the Makefile):  

Open a new terminal in the **fibonacci-js-sui** directory:  
```bash
cd contract/outpost
make new-session
```   

Wait for the **Bridge** and **Fleet** to process the request. The system will first start the ABCI container and then compute the result, each taking several seconds depending on the machine's performance. Once you see a message like this in the Fleet terminal:

```
I[2025-04-22|08:10:27.694] Settlement sent succeed 
```

It indicates that the settlement was successful. Then, retrieve the result (expected to be `832040`) by running:  

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
