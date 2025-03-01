# Fibonacci

This demo showcases interaction with the Sparsity Platform. The application computes the Fibonacci function. Users can submit requests via the App smart contract, which forwards them to the Sparsity platform. The platform computes the result using the App ABCI core and settles the request back to the App smart contract.

# Running in Dev Box

The repository consists of two main sections: Contract and ABCI Core. Please refer to the setup details below.

## [Contract](./contract/README.md)

## [ABCI Core](./server/README.md)

# Deployment

## 1. Deploy the App Contract

```bash
# Navigate to the ./contract directory
cp .env.example.sepolia .env
# Fill in your deployer private key in the .env file
make sepolia-deploy
# Add the contract address to the .env file
```

## 2. Publish the App to a Public Docker Registry

```bash
docker build -t yourusername/your-image-name:tag .
docker push yourusername/your-image-name:tag
```

## 3. Update `dockerURI` and `dockerHash` in the .env File

```bash
# Retrieve the image digest
docker images --digests
```

## 4. Register Your Contract with the Sparsity Outpost Contract

```bash
make sepolia-register
```

## 5. Wait for Official Approval from Sparsity

## 6. Call Your Contract

```bash
make sepolia-fib
```

## 7. Wait for the Result and Check It

```bash
make sepolia-fib-result
```
 