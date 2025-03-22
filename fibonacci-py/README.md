
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

```bash
make -f Makefile_sepolia register-app
```  

### 5. Call Your Contract  

```bash
make -f Makefile_sepolia request-fib NUM=10
```  

The system will first start the ABCI container and then compute the result, with each step taking several seconds, depending on the allocated machine's performance.

### 6. Retrieve and Verify the Result  

```bash
make -f Makefile_sepolia fib-result NUM=10
```  

**Expected output:**  

```bash
832040
```  