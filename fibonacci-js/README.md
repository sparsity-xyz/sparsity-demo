
# Fibonacci  

This demo showcases interaction with the **Sparsity Platform**. The application computes the Fibonacci sequence, allowing users to submit requests via a smart contract. The contract forwards the requests to the Sparsity platform, which processes them using the **App ABCI core** and returns the results back to the smart contract.  

---

## Running the App Locally  

### Prerequisites  
- **OS:** macOS or Linux (Windows users should use WSL)  
- **Dependencies:**  
  - [Foundry](https://book.getfoundry.sh/) installed  
  - `npm` or `yarn` installed  

### 1. Build the Docker Image  

```bash
cd server
docker build -t abci-fib:latest .
```  

### 2. Start the Chain Node and Deploy the Smart Contract  

```bash
cd contract
npm install
cp .env.example .env
make node
```  

Ensure that blocks start building before proceeding.  

### 3. Start the Bridge  

```bash
docker pull sparsityxyz/bridge:latest

# macOS
docker run --rm -ti -e HOST=host.docker.internal sparsityxyz/bridge:latest

# Linux
docker run --rm -ti -e HOST=172.17.0.1 sparsityxyz/bridge:latest
```  

### 4. Start the Fleet  

#### Pull the Fleet Image  

```bash
docker pull sparsityxyz/fleet:latest
```  

#### Initialize Fleet  

```bash
# macOS
docker run -ti --rm \
    -v ./.data:/root/.fleet \
    -v /var/run/docker.sock:/var/run/docker.sock \
    sparsityxyz/fleet:latest fleet init --local

# Linux
docker run -ti --rm \
    -v ./.data:/root/.fleet \
    -v /var/run/docker.sock:/var/run/docker.sock \
    --add-host=host.docker.internal:172.17.0.1 \
    sparsityxyz/fleet:latest fleet init --local
```  

#### Register Fleet  

```bash
# macOS
docker run -ti --rm \
    -v ./.data:/root/.fleet \
    -v /var/run/docker.sock:/var/run/docker.sock \
    sparsityxyz/fleet:latest fleet register --ip 127.0.0.1

# Linux
docker run -ti --rm \
    -v ./.data:/root/.fleet \
    -v /var/run/docker.sock:/var/run/docker.sock \
    --add-host=host.docker.internal:172.17.0.1 \
    sparsityxyz/fleet:latest fleet register --ip 127.0.0.1
```  

#### Run Fleet  

```bash
# macOS
docker run -ti --rm \
    -v ./.data:/root/.fleet \
    -v /var/run/docker.sock:/var/run/docker.sock \
    sparsityxyz/fleet:latest fleet run

# Linux
docker run -ti --rm \
    -v ./.data:/root/.fleet \
    -v /var/run/docker.sock:/var/run/docker.sock \
    --add-host=host.docker.internal:172.17.0.1 \
    sparsityxyz/fleet:latest fleet run
```  

### 5. Interact with the Smart Contract  

To compute Fibonacci for a given number (e.g., `10`):  

```bash
make request-fib NUM=10
```  

Wait for the **bridge** and **fleet** to process the request, then retrieve the result:  

```bash
make fib-result NUM=10
```  

**Expected output:**  

```bash
55
```  

---

# Deployment  

### 1. Deploy the App Contract  

```bash
cd contract
cp .env.example.sepolia .env
# Fill in your deployer private key in the .env file
make sepolia-deploy
# Add the deployed contract address to the .env file
```  

### 2. Publish the App to a Public Docker Registry  

```bash
docker build -t yourusername/your-image-name:tag .
docker push yourusername/your-image-name:tag
```  

### 3. Update `dockerURI` and `dockerHash` in the `.env` File  

Retrieve the image digest:  

```bash
docker images --digests
```  

### 4. Register Your Contract with the Sparsity Outpost Contract  

```bash
make base-sepolia-register
```  

### 5. Wait for Official Approval from Sparsity  

### 6. Call Your Contract  

```bash
make base-sepolia-fib
```  

### 7. Retrieve and Verify the Result  

```bash
make base-sepolia-fib-result
```  
 