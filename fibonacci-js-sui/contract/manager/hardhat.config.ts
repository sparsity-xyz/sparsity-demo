import { HardhatUserConfig } from "hardhat/config";
import "@nomicfoundation/hardhat-toolbox";
import '@openzeppelin/hardhat-upgrades';
import '@nomicfoundation/hardhat-verify';

import dotenv from 'dotenv';
dotenv.config();

if (!process.env.PROXY_ADMIN_PRIVATE_KEY) {
  throw new Error("PROXY_ADMIN_PRIVATE_KEY environment variable is not set");
}
if (!process.env.CONTRACT_OWNER_PRIVATE_KEY) {
  throw new Error("CONTRACT_OWNER_PRIVATE_KEY environment variable is not set");
}

const accounts = [
  process.env.PROXY_ADMIN_PRIVATE_KEY,
  process.env.CONTRACT_OWNER_PRIVATE_KEY
];

const customChainId = Number(process.env.CHAIN_ID);

const config: HardhatUserConfig = {
  solidity: {
    compilers: [
      {
        version: "0.8.27", // your default version
        settings: {
          optimizer: {
            enabled: false // default is not optimized
          }
        }
      }
    ],
    overrides: {
      // Path to the specific contract you want to optimize
      "contracts/CertManager.sol": {
        version: "0.8.27",
        settings: {
          optimizer: {
            enabled: true,
            runs: 200
          }
        }
      },
      "contracts/NitroValidator.sol": {
        version: "0.8.27",
        settings: {
          optimizer: {
            enabled: true,
            runs: 200
          }
        }
      },
      "contracts/Outpost.sol": {
        version: "0.8.27",
        settings: {
          optimizer: {
            enabled: true,
            runs: 200
          }
        }
      }
    }
  },
  paths: {
    sources: "./contracts",
    tests: "./test",
    cache: "./cache",
    artifacts: "./artifacts"
  },
  networks: {
    hardhat: {
      chainId: 31337,
      mining: {
        auto: false,
        interval: 1000
      },
      blockGasLimit: 120000000,
      allowUnlimitedContractSize: true
    },
    "chain": {
      url: process.env.CHAIN_RPC || "",
      accounts: accounts,
    },
  },
  etherscan: {
    apiKey: {
      "chain": process.env.ETHERSCAN_API_KEY || "",
    },
    customChains: [
      {
        network: "chain",
        chainId: customChainId,
        urls: {
          apiURL: process.env.CHAIN_EXPLORER_API || "",
          browserURL: process.env.CHAIN_EXPLORER_BROWSER || ""
        }
      }
    ]
  },
  sourcify: {
    enabled: true
  }
};



export default config;
