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

- [**Fibonacci JS**](./fibonacci-js/README.md)  
- [**Fibonacci Python**](./fibonacci-py/README.md)  
- [**Gomoku JS**](./gomoku-js/README.md)  
- [**AG2 Python**](./ag2-py)  

## Development Contribution  
### Setup & Commit Guidelines  
Before committing, always install dependencies in the **root directory**:  

```sh
npm i
```  

We enforce structured commit messages using **Commitlint**, **Husky**, and **Commitizen**.  
Use the following command for commits:  

```sh
git cz
```  

This ensures consistency and adherence to our commit conventions.

---  

For more details, refer to the official [Sparsity documentation](https://sparsity.gitbook.io/sparsity-platform).  

