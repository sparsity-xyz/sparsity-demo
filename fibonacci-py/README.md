
# Fibonacci  

This demo showcases interaction with the **Sparsity Platform**. The application computes the Fibonacci sequence, allowing users to submit requests via a smart contract. The contract forwards these requests to the **Sparsity platform**, which processes them using the **App ABCI core** and returns the results back to the smart contract.  

---

## Running the App Locally  

### Prerequisites  
- **OS:** macOS or Linux (Windows users should use WSL)  
- **Dependencies:**  
  - [Foundry](https://book.getfoundry.sh/) installed  
  - `npm` or `yarn` installed  

### 1. Build the Docker Image  
The Docker image contains the ABCI core, encapsulating all computation and execution logic.  

```bash
cd server
docker build -t abci-fib-py:latest .
```  

### 2. Start the Chain Node and Deploy the Smart Contract  
Simulates an EVM chain locally and deploys the smart contract.  

```bash
cd contract
npm install
cp .env.example .env
make node
```  

Wait until blocks start building before proceeding. Check the terminal output to ensure blocks are being produced.

### 3. Start the Bridge  
The Bridge service connects the host EVM chain with the Sparsity platform.  

```bash
docker pull sparsityxyz/bridge:latest

# macOS
docker run --rm -ti -e HOST=host.docker.internal sparsityxyz/bridge:latest

# Linux
docker run --rm -ti -e HOST=172.17.0.1 sparsityxyz/bridge:latest
```  

### 4. Start the Fleet  
The Fleet service is responsible for triggering the Sparsity execution session upon receiving signals from the host chain via the Bridge service.  

#### Pull the Fleet Images  

```bash
docker pull sparsityxyz/fleet:latest
docker pull sparsityxyz/fleet-er:latest
```  

#### Run Fleet  

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

### 5. Interact with the Smart Contract  
Now that everything is running locally, you can perform end-to-end testing by interacting with the smart contract.  

To compute Fibonacci for a given number (e.g., `10`):  

```bash
make request-fib NUM=10
```  

Wait for the **Bridge** and **Fleet** to process the request, then retrieve the result:  

```bash
make fib-result NUM=10
```  

**Expected output:**  

```bash
55
```  

---

# Deployment to devnet

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
