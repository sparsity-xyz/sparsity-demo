# Fibonacci  

This demo showcases interaction with the Sparsity Platform. The application computes the Fibonacci sequence. Users submit requests via the App smart contract, which forwards them to the Sparsity platform automatically. The platform processes the request using the App ABCI core and returns the result to the App smart contract.  

## Running the App End-to-End in a Local Dev Environment  

### Prerequisites  
- OS: macOS or Linux (Windows users should use WSL)  
- [Foundry](https://book.getfoundry.sh/) installed  
- npm or yarn installed  

### 1. Build the Docker Image  

```bash
docker build -t abci-fib:latest .
```  

### 2. Start the Chain Node and Deploy the Smart Contract  

```bash
cd contract
npm install
cp .env.example .env
make node
```  

### 3. Start the Bridge  

```bash
docker pull sparsityxyz/bridge
docker run sparsityxyz/bridge
```  

### 4. Start the Fleet  

```bash
docker pull sparsityxyz/fleet
docker run sparsityxyz/fleet
```  

### 5. Interact with the Smart Contract  

To compute Fibonacci for a given number (e.g., `num = 10`):  

```bash
make request-fib NUM=10
```  

### 6. Check the Result  

Wait for the bridge and fleet to settle the result, then retrieve it:  

```bash
make fib-result NUM=10
```  

Expected output:  

```bash
55
```  

---

# Deployment  

## 1. Deploy the App Contract  

```bash
# Navigate to the ./contract directory
cp .env.example.sepolia .env
# Fill in your deployer private key in the .env file
make sepolia-deploy
# Add the deployed contract address to the .env file
```  

## 2. Publish the App to a Public Docker Registry  

```bash
docker build -t yourusername/your-image-name:tag .
docker push yourusername/your-image-name:tag
```  

## 3. Update `dockerURI` and `dockerHash` in the `.env` File  

Retrieve the image digest:  

```bash
docker images --digests
```  

## 4. Register Your Contract with the Sparsity Outpost Contract  

```bash
make base-sepolia-register
```  

## 5. Wait for Official Approval from Sparsity  

## 6. Call Your Contract  

```bash
make base-sepolia-fib
```  

## 7. Wait for the Result and Check It  

```bash
make base-sepolia-fib-result
```  
 