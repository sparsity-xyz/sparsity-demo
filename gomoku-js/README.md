# Gomoku

This demo app allows users to start and join Gomoku games via the App smart contract. The game interacts with the ABCI core for gameplay, and the final results are settled back to the App smart contract.

## Components

The demo consists of three main sections:

### 1. [App Smart Contract](./contract)  
### 2. [App ABCI Core](./server)  
### 3. [App ABCI Client](./client)  

## Setup Guide
Follow these steps to set up and run the app locally.

### 1. Build the Docker Image
   a) Navigate to the server directory:
   ```bash
   cd server
   ```
   b) Build the Docker image:
   ```bash
   docker build -t abci-gomoku .
   ```

### 2. Start the Chain Node and Deploy the Smart Contract  
   a) Navigate to the contract directory:
   ```bash
   cd contract
   ```
   b) Install dependencies:
   ```bash
   npm install
   ```
   c) Copy the environment file:
   ```bash
   cp .env.example .env
   ```
   d) Start the node:
   ```bash
   make node
   ```
   e) Wait until blocks start building before proceeding. Check the terminal output to ensure blocks are being produced.

### 3. Start the Bridge  
   a) Pull the latest Bridge service image:
   ```bash
   docker pull sparsityxyz/bridge:latest
   ```
   b) Run the Bridge service:
   ```bash
   # macOS
   docker run --rm -ti -e HOST=host.docker.internal sparsityxyz/bridge:latest

   # Linux
   docker run --rm -ti -e HOST=172.17.0.1 sparsityxyz/bridge:latest
   ```

### 4. Start the Fleet  
   a) Pull the Fleet image:
   ```bash
   docker pull sparsityxyz/fleet:latest
   docker pull sparsityxyz/fleet-er:latest
   ```
   b) Initialize Fleet:
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
   c) Register Fleet:
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
   d) Run Fleet:
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

### 5. Start the Client  
   a) Navigate to the `client` folder:
   ```bash
   cd client
   ```
   b) Install dependencies:
   ```bash
   npm install
   ```
   c) Copy the environment file:
   ```
   cp .env.example .env
   ```
   Create a project in [Reown](https://reown.com/blog/how-to-get-started-with-appkit) and fill in the `VITE_PROJECT_ID` in the `.env` file.
   d) Run the app:
   ```bash 
   npm run dev
   ```
   e) You can now play the game locally at [http://localhost:5173](http://localhost:5173)!

### 6. Interact with the Client  
   a) **Test Addresses**
   ```
   Address 1: 0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266
   Private Key: 0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80

   Address 2: 0x70997970C51812dc3A010C7d01b50e0d17dc79C8
   Private Key: 0x59c6995e998f97a5a0044966f0945389dc9e86dae88c7a8412f4603b6b78690d
   ```
   b) **Connect Wallet**
   - Open [http://localhost:5173](http://localhost:5173) in your browser.
   - Connect wallet `0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266`.
   
   c) **Join Game**
   - Click the **Join Game** button and sign the transaction.
   - Ensure it is connected to the **Localhost** chain.

   d) **Open Another Session & Join with a Different Address**
   - Use a different browser session.
   - Connect with address `0x70997970C51812dc3A010C7d01b50e0d17dc79C8`.
   - Join the game.

   e) **Play the Game**
   - Play between two browser sessions.
   - Wait for the game to be settled on-chain.
   - Check on-chain results in the smart contract. 

