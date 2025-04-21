# Contract Deployment Guide

## Configuration

All network configurations are stored in `config/networks.json`. The configuration includes:
- Chain IDs
- RPC URLs
- Explorer APIs
- Explorer Browser URLs
- Secret mappings

### Network Configuration Structure
```json
{
  "networks": {
    "network_name": {
      "chain_id": 123,
      "rpc_url": "https://...",
      "explorer_api": "https://...",
      "explorer_browser": "https://...",
      "secrets": {
        "secret_name": "aws_secret_name",
        "secret_keys_mapping": {
          "proxy_admin_private_key": "PROXY_ADMIN_PRIVATE_KEY_EVM",
          "contract_owner_private_key": "CONTRACT_OWNER_PRIVATE_KEY_EVM"
        }
      }
    }
  }
}
```

### Adding New Networks
When adding a new network:
1. Follow the existing naming convention (e.g., `{chain}_{network}_{environment}`).
2. Add all required configuration fields.
3. Update the secret mappings in AWS Secrets Manager.

## Security

### Secret Management
- All private keys and sensitive data are stored in AWS Secrets Manager.
- Secrets are dynamically fetched during deployment.
- **Never** commit secrets to the repository.
- Use AWS Secrets Manager for all sensitive data.

### Deployment Process
1. The deployment script reads network configuration from `networks.json`.
2. Fetches required secrets from AWS Secrets Manager.
3. Generates a temporary `.env` file for deployment.
4. Cleans up sensitive data after deployment.

## Deployment Options

### Available Networks
- Ethereum Sepolia Devnet: `ethereum_sepolia_devnet`
- Ethereum Sepolia Staging: `ethereum_sepolia_staging`
- Optimism Sepolia Devnet: `optimism_sepolia_devnet`
- Optimism Sepolia Staging: `optimism_sepolia_staging`
- Base Sepolia Devnet: `base_sepolia_devnet`
- Base Sepolia Staging: `base_sepolia_staging`

### Deployment Steps

#### 1. Deploy Outpost
```bash
make -f Makefile_deploy deploy-outpost \
  network=<network_name>
```
For example:
```bash
make -f Makefile_deploy deploy-outpost \
  network=ethereum_sepolia_staging
```
Expected output:
```
Deployed Addresses

OutpostProxyModule#Outpost - 0x7f8f83fAf682C6032B89C86cda90e8fB8b94a5bF
OutpostProxyModule#TransparentUpgradeableProxy - 0x337cf856A9fe13d9d2a3cC40b7c514AeeF4079ae
OutpostProxyModule#ProxyAdmin - 0xF71E5506CDC7cE49242e574A37F53191D73c9f73
OutpostModule#Outpost - 0x337cf856A9fe13d9d2a3cC40b7c514AeeF4079ae
```
`OutpostModule#Outpost` will be used in later bridge and fleet related deployment.

#### 2. Deploy Manager
```bash
make -f Makefile_deploy deploy-manager \
  network=<network_name>
```
For example:
```bash
make -f Makefile_deploy deploy-manager \
  network=optimism_sepolia_staging
```
Expected output:
```
Deployed Addresses

ManagerProxyModule#Manager - 0x98A1B4BD79bb0CB0A0b304cd74a60699652DFDDa
ManagerProxyModule#TransparentUpgradeableProxy - 0x0A93c20F5361857c42d26096689d51a9048284F6
ManagerProxyModule#ProxyAdmin - 0xD65E0AA31C03Ea42E7B75CBf61d724CD1DaB3452
ManagerModule#Manager - 0x0A93c20F5361857c42d26096689d51a9048284F6
```
`ManagerModule#Manager` will be used in later bridge and fleet deployment.

##### Upgrading Existing Contracts (TODO: to be verified)
If you want to reuse the original proxy contract, you should update the contracts:
```bash
make -f Makefile_deploy upgrade-outpost \
  network=<network_name>
make -f Makefile_deploy upgrade-manager \
  network=<network_name>
```

#### 3. Deploy App Contract
You can deploy a sample app contract for testing and demo purposes:
```bash
make -f Makefile_deploy deploy-app \
  network=<network_name> \
  outpost=<outpost_proxy_contract>
```
For example:
```bash
make -f Makefile_deploy deploy-app \
  network=ethereum_sepolia_staging \
  outpost=0x337cf856A9fe13d9d2a3cC40b7c514AeeF4079ae
```
Expected output:
```
Deployed Addresses

appModule#APP - 0xbe74c49Fd50ca07CF5218478d1797acAb9D00de9
```

#### 4. Register the Example App in Outpost
```bash
make -f Makefile_deploy register-app \
  network=<network_name> \
  outpost=<outpost_proxy_contract> \
  app=<app_contract> \
  docker-uri=<docker_uri> \
  docker-hash=<docker_hash>
```
For example:
```bash
make -f Makefile_deploy register-app \
  network=ethereum_sepolia_staging \
  outpost=0x337cf856A9fe13d9d2a3cC40b7c514AeeF4079ae \
  app=0xbe74c49Fd50ca07CF5218478d1797acAb9D00de9 \
  docker-uri=sparsityxyz/abci-fib \
  docker-hash=sha256:d10e26f90061400174e3f48f16da183c5ea2e2595c1fb050edfae1cdd4322f21
```

#### 5. Approve the Example App
```bash
make -f Makefile_deploy approve-app \
  network=<network_name> \
  outpost=<outpost_proxy_contract> \
  app=<app_contract>
```
For example:
```bash
make -f Makefile_deploy approve-app \
  network=ethereum_sepolia_staging \
  outpost=0x337cf856A9fe13d9d2a3cC40b7c514AeeF4079ae \
  app=0xbe74c49Fd50ca07CF5218478d1797acAb9D00de9
```
**Note:** `_approvalCheck` in the outpost contract can bypass approval checks in devnet.

#### 6. Set Bridges Between Outpost and Manager Contract
##### 6.1 Set Bridge in Outpost
```bash
make -f Makefile_deploy set-outpost-bridge \
  network=<network_name> \
  outpost=<outpost_proxy_contract> \
  bridge-operator=<bridge_operator_contract>
```
For example:
```bash
make -f Makefile_deploy set-outpost-bridge \
  network=ethereum_sepolia_staging \
  outpost=0x337cf856A9fe13d9d2a3cC40b7c514AeeF4079ae \
  bridge-operator=0x1dcE29D7a307a05c83C3C5fD15dF1A10ceD0F6c4
```
##### 6.2 Set Bridge in Manager
```bash
make -f Makefile_deploy set-manager-bridge \
  network=<network_name> \
  manager=<manager_proxy_contract> \
  bridge-operator=<bridge_operator_contract> \
  outpost-chain-id=<outpost_chain_id>
```
For example:
```bash
make -f Makefile_deploy set-manager-bridge \
  network=optimism_sepolia_staging \
  manager=0x0A93c20F5361857c42d26096689d51a9048284F6 \
  bridge-operator=0x1dcE29D7a307a05c83C3C5fD15dF1A10ceD0F6c4 \
  outpost-chain-id=11155111
```

## GitHub Actions
Deployment workflows are available in `.github/workflows/`:
- `contract-outpost.yml`: Deploy Outpost contract.
- `contract-manager.yml`: Deploy Manager contract.

These workflows:
- Can be triggered manually.
- Require AWS credentials as secrets.
- Support multiple networks.
- Follow security best practices.

