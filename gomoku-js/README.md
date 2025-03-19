# Gomoku  

This demo application enables users to start and join **Gomoku** games via the App smart contract. The game logic interacts with the **ABCI core**, and final results are settled back to the App smart contract.  

## Components  

The demo consists of three main parts:  

1. **[App Smart Contract](./contract)** – Handles game logic and interactions on-chain.  
2. **[App ABCI Core](./server)** – Processes game moves and logic execution.  
3. **[App ABCI Client](./client)** – Provides a user-friendly interface for gameplay.  

---

## Setup Guide  

Follow these steps to set up and run the app locally.  

### Prerequisites  

- **OS:** macOS or Linux (Windows users should use WSL)  
- **Dependencies:**  
  - [Foundry](https://book.getfoundry.sh/) installed  
  - `npm` or `yarn` installed  
  - **Docker**: Ensure the Docker service is installed and running before proceeding  

---

### 1. Build the Docker Image  

Navigate to the `server` directory and build the Docker image:  

```bash
cd server
docker build -t abci-gomoku .
```  

---

### 2. Start the Chain Node and Deploy the Smart Contract  

Navigate to the `contract` directory:  

```bash
cd contract
```  

Install dependencies:  

```bash
npm install
```  

Set up environment variables:  

```bash
cp .env.example .env
```  

Start the node:  

```bash
make node
```  

Wait until blocks start building before proceeding. Check the terminal output to ensure blocks are being produced.  

---

### 3. Start the Bridge  

Pull the latest **Bridge** service image:  

```bash
docker pull sparsityxyz/bridge:latest
```  

Run the Bridge service:  

```bash
# macOS
docker run --rm -ti -e HOST=host.docker.internal sparsityxyz/bridge:latest

# Linux
docker run --rm -ti -e HOST=172.17.0.1 sparsityxyz/bridge:latest
```  

---

### 4. Start the Fleet  

Pull the **Fleet** images:  

```bash
docker pull sparsityxyz/fleet:latest
docker pull sparsityxyz/fleet-er:latest
```  

Run the Fleet service:  

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

---

### 5. Start the Client  

Navigate to the `client` folder:  

```bash
cd client
```  

Install dependencies:  

```bash
npm install
```  

Set up environment variables:  

```bash
cp .env.example .env
```  

Create a project in **[Reown](https://reown.com/blog/how-to-get-started-with-appkit)** and update the `.env` file with your `VITE_PROJECT_ID`.  

Run the app:  

```bash
npm run dev
```  

The game will now be available at **[http://localhost:5173](http://localhost:5173)**.  

---

### 6. Interact with the Client  

#### a) Test Addresses  

```plaintext
Address 1: 0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266
Private Key: 0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80

Address 2: 0x70997970C51812dc3A010C7d01b50e0d17dc79C8
Private Key: 0x59c6995e998f97a5a0044966f0945389dc9e86dae88c7a8412f4603b6b78690d
```  

#### b) Connect Wallet  

1. Open **[http://localhost:5173](http://localhost:5173)** in your browser.  
2. Connect with wallet `0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266`.  

#### c) Join a Game  

- Click **Join Game** and sign the transaction.  
- Ensure you are connected to the **Localhost** chain.  

#### d) Open Another Session & Join with a Different Address  

- Open another browser session.  
- Connect with address `0x70997970C51812dc3A010C7d01b50e0d17dc79C8`.  
- Join the game.  

#### e) Play the Game  

- Take turns playing between two browser sessions.  
- Wait for the game to be settled on-chain (reflected on UI).  


