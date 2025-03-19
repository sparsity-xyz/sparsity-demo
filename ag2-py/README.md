# AG2  

This demo application allows users to start a chat with **[AG2](https://github.com/ag2ai/ag2)** via the App smart contract. The system interacts with the **ABCI core for AG2**, and the final hash of the messages is settled back to the App smart contract.  

## Components  

The demo consists of three main parts:  

1. **[App Smart Contract](./contract)** – Handles on-chain logic and message settlements.  
2. **[App ABCI Core](./server)** – Processes messages and logic execution.  
3. **[App ABCI Client](./client)** – Provides a user-friendly chat interface.  

---

## Setup Guide  

Follow these steps to set up and run the app locally.  

### Prerequisites  

- **OS:** macOS or Linux (Windows users should use WSL)  
- **Dependencies:**  
  - [Foundry](https://book.getfoundry.sh/) installed  
  - `npm` installed  
  - **Docker** installed and running  

---

### 1. Build the Docker Image  

Navigate to the `server` directory and generate your API key:  

```bash
cd server
cp api_key_example.json api_key.json
```  

Fill in the necessary fields in `api_key.json`. For a free API key, refer to [this guide](https://github.com/chatanywhere/GPT_API_free).  

Build the Docker image:  

```bash
docker build -t abci-ag2 .
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

Pull the **Fleet** image:  

```bash
docker pull sparsityxyz/fleet:latest
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

Create a project in **[Reown](https://reown.com/blog/how-to-get-started-with-appkit)** and update the `.env` file with your `VITE_PROJECT_ID`:  

```bash
VITE_PROJECT_ID=
```  

Run the app:  

```bash
yarn start
# or
npm run dev
```  

The chat application will now be available at **[http://localhost:5173](http://localhost:5173)**.  

---

### 6. Interact with the Client  

#### a) Test Address  

```plaintext
Address: 0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266
Private Key: 0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80
```  

#### b) Connect Wallet  

1. Open **[http://localhost:5173](http://localhost:5173)** in your browser.  
2. Connect with wallet `0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266`.  

#### c) Start Chat  

- Click the **Start Chat** button and sign the transaction.  
- Ensure you are connected to the **Localhost** chain.  

#### d) Wait for Session Setup  

- Wait for the session to be created.  
- Once the session is created, you will need to sign a message to log in.  

#### e) Send Messages  

- After logging in, you can start sending messages.  

#### f) Exit  

- Sending `exit` will end the chat session.  

#### g) Settlement  

- After sending `exit`, wait for the final result settlement on-chain.  

