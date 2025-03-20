
# Fibonacci  

This demo showcases interaction with the **Sparsity Platform**. The application computes the Fibonacci sequence, allowing users to submit requests via a smart contract. The contract forwards these requests to the **Sparsity platform**, which processes them using the **App ABCI core** and returns the results back to the smart contract.  

---

## Running the App Locally  

### Prerequisites  
- **OS:** macOS or Linux (Windows users should use WSL)  
- **Dependencies:**  
  - [Foundry](https://book.getfoundry.sh/) installed  
  - `npm` or `yarn` installed  
  - **Docker**: Ensure the Docker service is installed and running before proceeding.  

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

Once you see a consistent block mining signal in the terminal, like this:  

```
    Block Number: 36
    Block Hash: 0xf883b971d3024ebb9c2391eef0478a0b587ec3a58b1837b5a297b8028daaf116  
    Block Time: "Wed, 19 Mar 2025 23:07:42 +0000"  

    Block Number: 37  
    Block Hash: 0x973de0985c3e0aee02a8f2e78eb9d3301cfdda83812077bbbf27dc9bcc6df47e  
    Block Time: "Wed, 19 Mar 2025 23:07:43 +0000"  
```  

you can proceed to the next section.

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

To compute Fibonacci for a given number (e.g., `10`):  

Open a new terminal in the **fibonacci-js** directory:  
```bash
cd contract
make request-fib NUM=10
```   

Wait for the **Bridge** and **Fleet** to process the request. Once you see a message like this in the Fleet terminal:

```
I[2025-03-20|01:14:18.616] Settlement success                           hash=0xc58176e897f9755822bd6001e3e1fdb086d62ffcc846e6c873e4a70323262d4f
```

It indicates that the settlement was successful. Then, retrieve the result by running:  

```bash
make fib-result NUM=10
```  

**Expected output:**  

```bash
55
```  

---

## Deployment to Devnet  

### 1. Deploy the App Contract  

```bash
cd contract
cp .env.example.sepolia .env
# Fill in your deployer private key in the .env file
make -f Makefile_sepolia deploy
# Add the deployed contract address to the .env file
```  

### 2. Publish the App to a Public Docker Registry  

```bash
docker build --platform linux/amd64 -t yourusername/your-image-name:tag .
docker login
docker push yourusername/your-image-name:tag
```  

### 3. Update `dockerURI` and `dockerHash` in the `.env` File  

Retrieve the image digest:  

```bash
docker images --digests | grep yourusername/your-image-name
```  

### 4. Register Your Contract with the Sparsity Outpost Contract  

```bash
make -f Makefile_sepolia register-app
```  

### 5. Wait for Official Approval from Sparsity  

### 6. Call Your Contract  

```bash
make -f Makefile_sepolia request-fib NUM=10
```  

### 7. Retrieve and Verify the Result  

```bash
make -f Makefile_sepolia fib-result NUM=10
```  
