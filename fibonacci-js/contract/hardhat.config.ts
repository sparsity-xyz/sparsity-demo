import { HardhatUserConfig } from "hardhat/config";
import "@nomicfoundation/hardhat-toolbox";
import '@openzeppelin/hardhat-upgrades';
import '@nomicfoundation/hardhat-verify';

import dotenv from 'dotenv';
dotenv.config();

const accounts = [
  process.env.PROXY_ADMIN_PRIVATE_KEY,
  process.env.CONTRACT_OWNER_PRIVATE_KEY
].filter(Boolean) as string[];


const config: HardhatUserConfig = {
  solidity: "0.8.27",
  networks: {
    hardhat: {
      chainId: Number(process.env.HARDHAT_CHAIN_ID ?? 31337),
      mining: {
        auto: false,
        interval: 1000
      },
    },
    optimism_sepolia: {
      url: process.env.OPTIMISM_RPC,
      accounts: accounts,
    },
    base_sepolia: {
      url: process.env.BASE_RPC,
      accounts: accounts,
    }
  },
  etherscan: {
    apiKey: {
      base_sepolia: process.env.ETHERSCAN_API_KEY_BASE || "",
      optimism_sepolia: process.env.ETHERSCAN_API_KEY_OPTIMISM || "",
    },
    customChains: [
      {
        network: "base_sepolia",
        chainId: 84532,
        urls: {
          apiURL: "https://api-sepolia.basescan.org/api",
          browserURL: "https://sepolia.basescan.org/"
        }
      },
      {
        network: "optimism_sepolia",
        chainId: 11155420,
        urls: {
          apiURL: "https://api-sepolia-optimistic.etherscan.io/api",
          browserURL: "https://sepolia-optimism.etherscan.io/"
        }
      }
    ]
  },
  sourcify: {
    enabled: true
  }
};

export default config;
