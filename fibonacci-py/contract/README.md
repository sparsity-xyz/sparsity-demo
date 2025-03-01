# Contract  

The **Fibonacci Contract** is designed to calculate Fibonacci numbers.  
You can input a number by calling `requestFib(uint256)`, wait for the computation result from **Sparsity**, and then retrieve the `n`-th Fibonacci number by calling `getFibonacci(uint256)`.  

## Requirements  

Ensure you have the following dependencies installed before proceeding:  

1. [**Foundry**](https://book.getfoundry.sh/getting-started/installation) - Smart contract development framework  
2. [**Node.js**](https://nodejs.org/en/download) - JavaScript runtime  

## Setting Up a Local Network  

First, configure the environment variables:  

```sh
cp .env.example .env
```

Default contract addresses:  

```sh
// Default App Contract address
APP_CONTRACT=0x5FbDB2315678afecb367f032d93F642f64180aa3  
// Default Mock Sparsity Outpost address
OUTPOST_PROXY_CONTRACT=0xe7f1725E7734CE288F8367e1Bb143E90bb3F0512  
```

### Starting a Local Node  

Run the following command to start a local blockchain node:  

```sh
make node
```

---

## Testing  

### 1️⃣ Generating Initial Data  

The **initial data** is ABI-encoded and sent to the **ABCI Core**.  
To compute `fib(22)`, we encode `22` using `abi.encode(22)`.  

Use the following command to generate this encoded data outside the contract. The output can then be used as input for **ABCI Core** testing:  

```sh
make request-fib NUM=22
```

### 2️⃣ Settling the Result to the Contract  

The computed result of `fib(22)` must also be ABI-encoded. Retrieve the encoded result from your **ABCI Core** and run the following command to validate and settle it in the contract:  

```sh
make settle-result RESULT=0x000000000000000000000000000000000000000000000000000000000000452f NUM=22
```
