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

3. Start the outpost and app chain node (Sui) and deploy outpost and app contract

Open one terminal, start Sui local node
```
cd contract/sui
make node
```

Open another terminal, deploy the outpost contract
```
cd contract/sui

make faucet

make deploy-outpost

```
You should see something like this
```
Outpost Contract Deployed. Environment Variables:
OUTPOST_ADDR=0xcb5f8d32698ea486a15f1f4d2b0a2003417cc37fc6c8ba19f18ea877181b1026
OUTPOST_ADMIN_CAP=0xfcec673654c6a0829cd602062a03f4f87ced59f90c7431f49c3e443687158d21
OUTPOST_APP_REGISTRY=0x52ea4c53b27dca0642aa2e7cdad36730e96a1c919288400366471fdeba9acd48
OUTPOST_APP_SESSION=0xc92fc516d3477beb9ede4ca7c5150f814f798bdb5238aed27e21f3ae4d7fb128
```

Take the value of [OUTPOST_ADDR], fill that in sparsity address in fibonacci-js-sui\contract\outpost\app\Move.toml, like
```
[addresses]
sparsity = "0xcb5f8d32698ea486a15f1f4d2b0a2003417cc37fc6c8ba19f18ea877181b1026" 
app = "0x0"
```

Then deploy app address
```
make deploy-app
```

You would see 
```
App Contract Deployed. Environment Variables:
APP_ADDR=0xd76f76c9375ed07c8ad986388b4eff39e3a26b185746dc928b578831820ce736
APP_STATE=0xcffde70ac41413d8100095b4883b61446e24ad76d8d0da5ba1e7dab559dcfe56
```

Then register app and approve app
```
make register-app

make approve-app
```


### 3. Start the Bridge  
The **Bridge** service connects the host EVM chain with the **Sparsity platform**.  

Update [OutpostAddress] in `bridge/.env.example` with the value of [OUTPOST_ADDR], for example
```
OutpostAddress=0xcb5f8d32698ea486a15f1f4d2b0a2003417cc37fc6c8ba19f18ea877181b1026
```

Open a new terminal and run:  
```bash
docker pull sparsityxyz/bridge:20250420230231 
 
# macOS
docker run --rm -ti --env-file bridge/.env.example -e HOST=host.docker.internal sparsityxyz/bridge:20250420230231  

# Linux
docker run --rm -ti --env-file bridge/.env.example -e HOST=172.17.0.1 sparsityxyz/bridge:20250420230231 
```  



Once you see the following signal in the terminal, it indicates that the bridge service has started and is running. You can now proceed to the next section.  

```
Sui-Event-Query request: ...
```  


### 4. Start the Fleet  
The **Fleet** service triggers the Sparsity execution session upon receiving signals from the host chain via the Bridge service.  

Open a new terminal and pull the Fleet images:  
```bash
docker pull sparsityxyz/fleet:20250421141233
docker pull sparsityxyz/fleet-er:latest
```  

Then, run the Fleet service:  

```bash
# macOS
docker run -ti --rm \
    --env-file fleet/.env.example \
    -v /var/run/docker.sock:/var/run/docker.sock \
    sparsityxyz/fleet:20250421141233 fleet run --local

# Linux
docker run -ti --rm \
    --env-file fleet/.env.example \
    -v /var/run/docker.sock:/var/run/docker.sock \
    --add-host=host.docker.internal:172.17.0.1 \
    sparsityxyz/fleet:20250421141233 fleet run --local
```  

Once the following signal appears in the terminal, it confirms that the fleet service has successfully started and is running. You can now proceed to the next section.  

```
I[2025-03-19|23:19:33.317] All historical data processed                module=eventListener 
```  

### 5. Interact with the Smart Contract  
Once everything is running locally, you can perform end-to-end testing by interacting with the smart contract.  

To compute Fibonacci for a given number (e.g., `30`):  

Open a new terminal in the **fibonacci-js** directory:  
```bash
cd contract
make request-fib NUM=30
```   

Wait for the **Bridge** and **Fleet** to process the request. The system will first start the ABCI container and then compute the result, each taking several seconds depending on the machine's performance. Once you see a message like this in the Fleet terminal:

```
I[2025-03-20|01:14:18.616] Settlement success                           hash=0xc58176e897f9755822bd6001e3e1fdb086d62ffcc846e6c873e4a70323262d4f
```

It indicates that the settlement was successful. Then, retrieve the result by running:  

```bash
make fib-result NUM=30
```  

**Expected output:**  

```bash
832040
```  

---

## Deployment to Devnet  

### 1. Deploy the App Contract  

Open a new terminal in the **fibonacci-js** directory:

```bash
cd contract
cp .env.example.sepolia .env
```

Next, update the `.env` file by adding your deployer private key.

**Note:** The Base Sepolia RPC endpoint may sometimes be unstable. If you encounter issues, try different endpoints from [Chainlist](https://chainlist.org/chain/84532) and update the `BASE_RPC` variable in your `.env` file accordingly.

To deploy the contract, run:  
```bash
make -f Makefile_sepolia deploy
```

The deployment files will be stored in:  
```  
ignition/deployments/chain-84532  
```  

During deployment, you could be prompted with the following options in the terminal. Select **"yes"** for both:  
```  
✔ Confirm deploy to network base_sepolia (84532)? … yes  
✔ Confirm reset of deployment "chain-84532" on chain 84532? … yes  
```  

Afterwards, add the deployed contract address to your `.env` file:
```
APP_CONTRACT=
```

### 2. Publish the App to a Public Docker Registry  

Refer to [Docker's official guide](https://docs.docker.com/get-started/introduction/build-and-push-first-image/) for instructions on building and pushing a Docker image.  

#### Build the Docker Image  

```bash
cd server
docker build --platform linux/amd64 -t <DOCKER_USERNAME>/<REPOSITORY_NAME>:<TAG> .
```  

This builds a Docker image with the specified tag, ensuring compatibility with `linux/amd64`.  

#### Log in to Docker Registry  

```bash
docker login
```  

Authenticate with the registry before pushing the image.  

#### Push the Image to the Registry  

```bash
docker push <DOCKER_USERNAME>/<REPOSITORY_NAME>:<TAG>
```  

This uploads the image to the specified repository.  

---

### 3. Update Docker Information  

Refer to the [Docker documentation](https://docs.docker.com/reference/cli/docker/image/ls/#digests) for details on retrieving the image digest.  

#### Retrieve the Image Digest and Update the `.env` File  

```bash
docker images --digests | grep <DOCKER_USERNAME>/<REPOSITORY_NAME>
```  

From the terminal output, locate the row where the **[REPOSITORY]** column matches `<DOCKER_USERNAME>/<REPOSITORY_NAME>`. The value in the **[DIGEST]** column is the Docker image hash (`DOCKER_HASH`), and the **[REPOSITORY]** column provides the `DOCKER_URI`.  

Update the `.env` file with these values:  

```
DOCKER_URI=<REPOSITORY_NAME>
DOCKER_HASH=<IMAGE_DIGEST>
```

### 4. Register Your Contract with the Sparsity Outpost Contract  

Open a new terminal in the **fibonacci-js** directory:

```bash
cd contract
make -f Makefile_sepolia register-app
```  

### 5. Call Your Contract  

In contract directory
```bash
make -f Makefile_sepolia request-fib NUM=30
```  

The system will first start the ABCI container and then compute the result, with each step taking several seconds, depending on the allocated machine's performance.

### 6. Retrieve and Verify the Result  

In contract directory
```bash
make -f Makefile_sepolia fib-result NUM=30
```  

**Expected output:**  

```bash
832040
```  