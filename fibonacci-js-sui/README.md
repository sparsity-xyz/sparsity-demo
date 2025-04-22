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

make faucet

make deploy-outpost

```
You should see something like this
```
Outpost Contract Deployed. Environment Variables:
OUTPOST_ADDR=0x1d28e52283bc200f29024286f35ac573524a29ddeb1b748a9af34dfad6bc3490
OUTPOST_ADMIN_CAP=0x9553a8f841f3e19962e0917853030ec04efadcebd5c8c16947ce423672918c4a
OUTPOST_APP_REGISTRY=0xfa3b71c7fc34ecdf4619d6240e5ca08f67cae246c7e3a61c8689ba8f8dd8fa13
OUTPOST_APP_SESSION=0x1136159c597b16d35fb1a2f54391d253544a8a31afb13939b3a8316a7b74f973
```

Take the value of [OUTPOST_ADDR], fill that in sparsity address in fibonacci-js-sui\contract\outpost\app\Move.toml, like
```
[addresses]
sparsity = "0x1d28e52283bc200f29024286f35ac573524a29ddeb1b748a9af34dfad6bc3490" 
app = "0x0"
```

Then deploy app address in the same terminal
```
make deploy-app
```

You would see 
```
App Contract Deployed. Environment Variables:
APP_ADDR=0xfed750fb2ca15068425e66559a0e64189b2055838f5406893917ba04582afe58
APP_STATE=0x82e89202674c2b2e70f7c8e63739466e4c0d09ee96da23d4986be196c6c1cb07
```

Then register app and approve app in the same terminal
```
make register-app && make approve-app
```


### 4. Start the Bridge  
The **Bridge** service connects the host EVM chain with the **Sparsity platform**.  

Update [OutpostAddress] in `bridge/.env.example` with the value of [OUTPOST_ADDR], for example
```
OutpostAddress=0x1d28e52283bc200f29024286f35ac573524a29ddeb1b748a9af34dfad6bc3490
```

Open a new terminal, go to **fibonacci-js-sui** directory:  
```bash
docker pull sparsityxyz/bridge:20250420230231 
 
# macOS and wsl
docker run --rm -ti --env-file bridge/.env.example -e HOST=host.docker.internal sparsityxyz/bridge:20250420230231  

# Linux
docker run --rm -ti --env-file bridge/.env.example -e HOST=172.17.0.1 --add-host=host.docker.internal:host-gateway sparsityxyz/bridge:20250420230231 
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
