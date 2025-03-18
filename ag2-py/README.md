# AG2

This demo app allows users to start a chat with [AG2](https://github.com/ag2ai/ag2) via the App smart contract. The demo interacts with the ABCI core for AG2, and the final hash of the messages are settled back to the App smart contract.

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
   b) Generate your api key (see [here](https://github.com/chatanywhere/GPT_API_free) for a free api key):
   ```bash
   cp api_key_example.json api_key.json
   // fill the fields in api_key.json
   ```
   c) Build the Docker image:
   ```bash
   docker build -t abci-ag2 .
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
   d) Run Fleet (whitelisting two addresses):
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
   c) Create a project in [Reown](https://reown.com/blog/how-to-get-started-with-appkit) and fill in the `VITE_PROJECT_ID` in the `.env` file:
   ```
   VITE_PROJECT_ID=
   ```
   d) Run the app:
   ```bash
   yarn start
   # or
   npm run dev
   ```
   e) You can now play the game locally at [http://localhost:5173](http://localhost:5173)!

### 6. Interact with the Client  
    
   a) **Test Address**
   ```
   Address 1: 0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266
   Private Key: 0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80
   ```
   b) **Connect Wallet**
   - Open [http://localhost:5173](http://localhost:5173) in your browser.
   - Connect wallet `0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266`.
   
   c) **Start Chat**
   - Click the **Star Game** button and sign the transaction.
   - Ensure it is connected to the **Localhost** chain.

   d) **Wait for the session setup**
   - Wait for the session created, after session created, you will sign a message to login.

   e) **Send the messages**
   - After login, you can send the messages.

   f) **Exit**
   - Send `exit` will finish the chat

   g) **Settlement**
   - After sending `exit`, waiting for the result settlement
