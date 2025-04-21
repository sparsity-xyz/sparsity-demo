To install **Sui Full Node** on Windows, follow these steps carefully. Since Sui nodes run in a Linux-like environment, you’ll need **Windows Subsystem for Linux (WSL)**.  

### **Step 1: Install Windows Subsystem for Linux (WSL)**
1. Open **PowerShell** as Administrator and run:  
   ```powershell
   wsl --install
   ```
2. Restart your computer if prompted.
3. Install **Ubuntu** from the Microsoft Store.

---

### **Step 2: Set Up Dependencies**
1. Open **Ubuntu** from the Start menu.
2. Update packages:  
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```
3. Install required dependencies:  
   ```bash
   sudo apt install -y curl git clang build-essential libssl-dev pkg-config jq
   ```

---

### **Step 3: Install Rust**
1. Run the following command:  
   ```bash
   curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
   ```
2. Select **1** (default installation).
3. Reload environment variables:  
   ```bash
   source $HOME/.cargo/env
   ```

---

### **Step 4: Clone & Build Sui**
1. Clone the Sui repository:  
   ```bash
   git clone https://github.com/MystenLabs/sui.git
   cd sui
   ```
2. Check out the latest stable release:  
   ```bash
   git checkout devnet
   ```
3. Build Sui binaries:  
   ```bash
   cargo build --release
   ```

---

### **Step 5: Run Sui Full Node**
1. Download the full node configuration:  
   ```bash
   mkdir -p ~/sui-fullnode
   curl -o ~/sui-fullnode/fullnode.yaml https://github.com/MystenLabs/sui/blob/main/crates/sui-config/data/fullnode-template.yaml
   ```
2. Start the Sui Full Node:  
   ```bash
   ~/.cargo/bin/sui-node --config-path ~/sui-fullnode/fullnode.yaml
   ```

---

### **Step 6: Verify Installation**
- If the node starts syncing data, you have successfully set it up! 🎉
- To check logs, use:
  ```bash
  tail -f ~/.sui/sui.log
  ```

Let me know if you hit any issues! 🚀