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
npm install
```

### Starting a Local Node and deploy contract

Run the following command to start a local blockchain node:  

```sh
make node
```

Wait for all of the contracts are deployed and the node starts to mine blocks.