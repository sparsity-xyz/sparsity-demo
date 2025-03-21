
# Fibonacci  

This demo showcases interaction with the **Sparsity Platform**. The application computes the Fibonacci sequence, allowing users to submit requests via a smart contract. The contract forwards these requests to the Sparsity platform, which processes them using the **App ABCI core** and returns the results back to the smart contract.

The Fibonacci sequence is computed recursively in this demo, which makes it an intensive computation. This type of recursive calculation is not feasible to perform on-chain due to its resource requirements, but it serves as an excellent example of the computational power of Sparsity. By offloading this computation to Sparsity, we demonstrate the platform's ability to handle complex and resource-heavy tasks efficiently.
 
---

## Running the App Locally  

### Prerequisites  
- **OS:** macOS or Linux (Windows users should use WSL)
- **Dependencies:**  
  - [Foundry](https://book.getfoundry.sh/): Ethereum development toolchain for smart contract development
    ```bash
    curl -L https://foundry.paradigm.xyz | bash
    foundryup
    ```
  - Node.js package manager: Install either [npm](https://nodejs.org/) (comes with Node.js) or [yarn](https://yarnpkg.com/getting-started/install)
  - **Docker**: Container platform for running services
    - [Install Docker for Mac](https://docs.docker.com/desktop/install/mac-install/)
    - [Install Docker for Linux](https://docs.docker.com/engine/install/)
    - [Install Docker for Windows + WSL](https://docs.docker.com/desktop/windows/wsl/)

Make sure all services are properly installed and Docker daemon is running before proceeding with the setup.

### Project Structure
.
├── README.md                     # Project documentation
├── contract                      # Smart contract-related files
│   ├── Makefile                  # Build automation script
│   ├── Makefile_sepolia          # Build script for Sepolia testnet
│   ├── contracts                 # Solidity smart contracts
│   │   ├── Manager.sol           # Contract for managing fleets
│   │   ├── Outpost.sol           # Contract for registration operations
│   │   ├── Proxy.sol             # Proxy contract for upgradeability
│   │   ├── app.sol               # Main application logic contract
│   │   └── util.sol              # Utility functions for contracts
│   ├── hardhat.config.ts         # Hardhat configuration for Ethereum development
│   ├── package.json              # Dependencies and scripts for contract development
│   └── tsconfig.json             # TypeScript configuration for contract project
└── server                        # Backend server code
    ├── Dockerfile                # Docker configuration for containerization
    ├── Makefile                  # Build automation for the ABCI
    ├── package.json              # Dependencies and scripts for the backend
    ├── src                       # Source code for the ABCI core
    │   └── index.ts              # Entry point for the ABCI core
    └── tsconfig.json             # TypeScript configuration for the ABCI core


### 1. Build the Docker Image  
The Docker image contains the ABCI core, encapsulating all computation and execution logic.  

Open a new terminal in the **fibonacci-js** directory:  
```bash
cd server
docker build -t abci-fib:latest .
```  

### 2. Start the Chain Node and Deploy the Smart Contract  
This step simulates an EVM chain locally and deploys the smart contract.  

Open a new terminal in the **fibonacci-js** directory:  
```bash
cd contract

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


### 3. Start the Bridge  
The **Bridge** service connects the host EVM chain with the **Sparsity platform**.  

Open a new terminal and run:  
```bash
docker pull sparsityxyz/bridge:latest

# macOS
docker run --rm -ti -e HOST=host.docker.internal sparsityxyz/bridge:latest

# Linux
docker run --rm -ti -e HOST=172.17.0.1 sparsityxyz/bridge:latest
```  

Once you see the following signal in the terminal, it indicates that the bridge service has started and is running. You can now proceed to the next section.  

```
I[2025-03-19|23:10:20.791] All historical data processed                module=eventListener 
```  


### 4. Start the Fleet  
The **Fleet** service triggers the Sparsity execution session upon receiving signals from the host chain via the Bridge service.  

Open a new terminal and pull the Fleet images:  
```bash
docker pull sparsityxyz/fleet:latest
docker pull sparsityxyz/fleet-er:latest
```  

Then, run the Fleet service:  

```bash
# macOS
docker run -ti --rm \
    -v /var/run/docker.sock:/var/run/docker.sock \
    sparsityxyz/fleet:latest fleet run --local

# Linux
docker run -ti --rm \
    -v /var/run/docker.sock:/var/run/docker.sock \
    --add-host=host.docker.internal:172.17.0.1 \
    sparsityxyz/fleet:latest fleet run --local
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
#### Build the Docker image  
Open a new terminal in the **fibonacci-js** directory:
```bash
cd server
docker build --platform linux/amd64 -t <registry>/<repository>:<tag> .
```
This builds a Docker image with the specified tag, ensuring compatibility with `linux/amd64`.  

#### Log in to Docker registry  
```bash
docker login
```
This authenticates you with the registry before pushing the image.  

#### Push the image to the registry  
```bash
docker push <registry>/<repository>:<tag>
```
This uploads the image to the specified repository.  

For more details, check the official Docker documentation:  
🔗 [Docker Push Documentation](https://docs.docker.com/engine/reference/commandline/push/)


### 3. Update the docker info
Update `dockerURI` and `dockerHash` in `.env` File 
```
DOCKER_URI=
DOCKER_HASH=
```

Retrieve the image digest and fill as `dockerHash`:  

```bash
docker images --digests | grep <registry>/<repository>
```  

### 4. Register Your Contract with the Sparsity Outpost Contract  

Open a new terminal in the **fibonacci-js** directory:

```bash
cd contract
make -f Makefile_sepolia register-app
```  

### 5. Wait for Official Approval from Sparsity   

For **devnet (Base Sepolia)** deployment in this demo, approval is **not required**—it will be approved automatically.  

(For **production**, you need to submit a request in the Sparsity support channel [here](https://discord.gg/PvS5yfPBwH) and contact a support engineer. Once approved, your DApp will be fully deployed.)


### 6. Call Your Contract  

In contract directory
```bash
make -f Makefile_sepolia request-fib NUM=30
```  

The system will first start the ABCI container and then compute the result, with each step taking several seconds, depending on the allocated machine's performance.

### 7. Retrieve and Verify the Result  

In contract directory
```bash
make -f Makefile_sepolia fib-result NUM=30
```  
