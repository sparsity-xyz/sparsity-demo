# Sparsity App Development  

[Sparsity](https://sparsity.gitbook.io/sparsity-platform) offers a decentralized platform with robust computational support, addressing both the trust challenges of decentralization and the computational limitations of blockchain technology.  

When developing an app or service on Sparsity, developers need to implement three core components:  

- **App Smart Contract**  
  - Initializes the mainnet on-chain configuration and data.  
  - Injects data into the Sparsity network.  
  - Receives and settles results from the Sparsity network.  

- **App ABCI Core**  
  - Receives data injected from the App Smart Contract.  
  - Executes processing and computations.  
  - Interacts with the App Client (if applicable) to collect interaction data and respond to user actions.  
  - Generates results to send back on-chain.  

- **App Client** (optional)  
  - Interacts with the smart contract for user sessions and authentication.  
  - Interfaces with the ABCI Core for interactions during app execution.  

This repository includes several full-stack demo applications built on the Sparsity platform.  

## Demo Applications  

- [**Fibonacci JS**](./fibonacci-js/README.md) – A "Hello World" introduction to Sparsity Platform
- [**Fibonacci Python**](./fibonacci-py/README.md) – Fibonacci computation with Python implementation
- [**Fibonacci SUI**](./fibonacci-js-sui/README.md) – Building on Sui: Smart contracts meet Sparsity
- [**Fibonacci TEE**](./fibonacci-js-tee/README.md) – Trusted Execution: Secure computing with Sparsity
- [**Gomoku JS**](./gomoku-js/README.md) – Interactive game development with Sparsity
- [**AG2 Python**](./ag2-py) – AI agent implementation with Sparsity Platform

## Development Contribution  
### Setup & Commit Guidelines  
Before committing, please always install dependencies in the **root directory**:  

```sh
npm i
```  

We kindly enforce structured commit messages using **Commitlint**, **Husky**, and **Commitizen** to keep our project consistent and easy to maintain. 

For a smooth and easy commit experience, simply use the following command:  

```sh
git cz
```  

If you're new to this, don't worry! Here's a helpful [Git Commitizen tutorial](https://github.com/commitizen/cz-cli) to get you started. Feel free to check it out!

--- 

For more details, refer to the official [Sparsity documentation](https://sparsity.gitbook.io/sparsity-platform).  

