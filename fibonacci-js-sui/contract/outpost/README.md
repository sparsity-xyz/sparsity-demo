
# High Level Design Flow

## Roles
- **Sparsity**: Platform provider, deploys and manages the outpost contract  
- **Provider**: App provider, deploys and manages individual app contracts  
- **User**: End user who interacts with apps  

## Contract Architecture
- **Outpost Contract**: Central registry for apps and sessions  
- **App Contract**: Individual app implementation with user session mapping  

## Flow

1. **Initial Setup**
   - Sparsity deploys outpost contract (address A)  
   - Provider deploys app contract (address B), taking outpost contract as its dependency  

2. **App Registration**
   - Provider registers their app (address B) in outpost contract  
   - Provider gives Sparsity (outpost owner) settlement capability  
   - Outpost maintains mapping: `[app_address => approval_status]`  
   - Sparsity reviews and approves/rejects apps  

3. **Session Creation**
   - User initiates session in app B  
   - App B updates mapping: `[user_address => session_id]`  
   - App B creates session mapping: `[session_id => session_details]`  
   - App B calls function in Outpost A, Outpost A creates session mapping: `[session_id => session_details]`, and emits `SessionStarted` event  

4. **Bridge Validation**
   - Bridge listens for `SessionStarted` events  
   - Validates if user session exists in app B  
   - Triggers fleet execution if valid  

5. **Result Updates**
   - Fleet updates result in session mapping in Outpost A (try until succeed)  
   - Fleet updates result in session mapping in app B (try and archive if failed)  

## Key Data Structures
- Outpost App Registry Table: `Table<address, App>`  
- Outpost Session Table: `Table<address, Table<u64, Session>>`  
- App User Table: `Table<address, u64>`  
- App Session Table: `Table<u64, Session>`  

---

# Local Quick Setup

This guide outlines the steps to set up a local Sui development environment, publish the Outpost contract, and interact with both bridge and fleet.

---

## 1. Contract Setup

### 1.1 Install Sui Binaries  
Follow the official Sui documentation to install the Sui CLI and necessary dependencies:  
🔗 [Sui Install Guide](https://docs.sui.io/guides/developer/getting-started/sui-install)

### 1.2 Start Local Sui Network  
Run a local Sui network with a faucet. The `--force-regenesis` flag ensures a clean state each time:  
```bash
RUST_LOG="off,sui_node=info" sui start --with-faucet --force-regenesis
```
Keep this terminal window open as it runs the local Sui network.

### 1.3 Fund Your Local Wallet  
Open a **new** terminal window. Use the faucet to get test SUI tokens:  
```bash
sui client faucet
```
You might need to run this multiple times to ensure enough gas.

### 1.4 Publish the Outpost Contract  
Navigate to the Outpost contract directory and publish it:  
```bash
cd contract/sui 
sui client publish --gas-budget 50000000 outpost
```

### 1.5 Extract and Store Object IDs  
Extract key IDs from the `publish` output and store them as environment variables for later use:

- **Identify the IDs:**
  - `PackageID: 0x...`
  - Shared objects like `<OUTPOST_ADDR>::outpost::AppRegistry: 0x...`
  - Objects transferred to you like `<OUTPOST_ADDR>::outpost::AdminCap: 0x...`

- **Set Environment Variables (example):**
```bash
export OUTPOST_ADDR=0xd1c7b737c8eef490fb0a8dd7f84741057072a5c740772b104e2e095aca34b4be
export OUTPOST_APP_REGISTRY=0x964086aa6f83f596bab8049ef56f11cdc15ac61450f3fda8dc00666650e70bef
export OUTPOST_APP_SESSION=0x54d6fe3fd7b9b11da15efbec25e7d77c5cb6b74f13558e21a90fda307b888f6d
export OUTPOST_ADMIN_CAP=0x4fc28e2859ee5b9cba365528cca625a7d5cd077925bb65cf9dbb203ef5d42b5b
```

> 🔔 Note: Environment variables are session-specific; re-export if you open a new terminal.

### 1.6 Publish App Contract  
Update the app's `Move.toml` file (`contract/sui/app/Move.toml`) with the correct OUTPOST_ADDR, which is just published in the former step:  
```toml
[addresses]
sparsity = <OUTPOST_ADDR>
```

Then publish the contract, in the directory `contract/sui`:  
```bash
sui client publish --gas-budget 50000000 app
```

- **Identify the IDs:**
  - `PackageID: 0x...`
  - Shared objects like `<APP_PACKAGE_ID>::app::State: 0x...`
  - Objects transferred to you like `<APP_PACKAGE_ID>::app::AdminCap: 0x...`

- **Set Environment Variables (example):**
```bash
export APP_ADDR=0x099aa4b7100169aef879cb987b69a67322872debfd400beaf4a08400f105b1ab
export APP_STATE=0x51b4f09e163f90873b07f939a6671fd79b6c54f75e4601c948d8c55a665399bb
```

Now the Outpost and App contracts are deployed, and you're ready to test.

**Examples:**
- Register the Fibonacci App:
```bash
sui client call --package $OUTPOST_ADDR --module outpost --function register_app --args $OUTPOST_APP_REGISTRY $APP_ADDR $APP_STATE 1 sparsityxyz/abci-fib sha256:d10e26f90061400174e3f48f16da183c5ea2e2595c1fb050edfae1cdd4322f21
```

- Approve App:
```bash
sui client call --package $OUTPOST_ADDR --module outpost --function approve_app --args $OUTPOST_ADMIN_CAP $OUTPOST_APP_REGISTRY $APP_ADDR
```

These exported values will be useful for bridge and fleet setup.

---

## 2. Bridge Setup

### 2.1 Setup Environment
```bash
cd ./bridge
cp .env.example .env
```

Set Sui environment values (not EVM):
```dotenv
OutpostChainId=10000000000000000000 
OutpostHTTP=http://127.0.0.1:9000
OutpostAddress=0xd1c7b737c8eef490fb0a8dd7f84741057072a5c740772b104e2e095aca34b4be
```

### 2.2 Download Dependencies
```bash
go mod download
```

### 2.3 Run Bridge
```bash
go run main.go
```

---

## 3. Fleet Setup

### 3.1 Setup Environment
```bash
cd ./fleet
cp .env.example .env
```

Update values:
```dotenv
SUI_OUTPOST_ADDRESS=0xd1c7b737c8eef490fb0a8dd7f84741057072a5c740772b104e2e095aca34b4be
SUI_OUTPOST_SESSION_ADDRESS=0x54d6fe3fd7b9b11da15efbec25e7d77c5cb6b74f13558e21a90fda307b888f6d
SUI_OUTPOST_ADMIN_CAP_ADDRESS=0x4fc28e2859ee5b9cba365528cca625a7d5cd077925bb65cf9dbb203ef5d42b5b
```

`SUI_OUTPOST_OWNER_MNEMONIC` is the mnemonic of your local active Sui address.  
Check by:
```bash
sui client active-address
```

### 3.2 Run Fleet
```bash
make run-fleet-local
```

---

## 4. Test Application

### 4.1 Create Session  
From a new terminal, trigger `create_session` in app contract B:
```bash
sui client call --package $APP_ADDR --module app --function create_session --args $OUTPOST_APP_REGISTRY $OUTPOST_APP_SESSION $APP_ADDR $APP_STATE 11
```

Check updates in **bridge** and **fleet** terminals. Results should settle in `OUTPOST_APP_SESSION`.

### 4.2 Check Result
```bash
sui client call --package $OUTPOST_ADDR --module outpost --function get_session_info --args $OUTPOST_APP_SESSION $APP_ADDR 0 --dev-inspect
```

Result will be in bytes format—requires client-side decoding.

---
 