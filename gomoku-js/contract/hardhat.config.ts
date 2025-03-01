import { HardhatUserConfig } from "hardhat/config";
import "@nomicfoundation/hardhat-toolbox";
import dotenv from 'dotenv';
dotenv.config();

const accounts = [
  process.env.DEPLOYER_PRIVATE_KEY,
].filter(Boolean) as string[];


const config: HardhatUserConfig = {
  solidity: "0.8.28",
  networks: {
    base_sepolia: {
      url: process.env.BASE_SEPOLIA_RPC || "",
      accounts: accounts,
    }
  },
};

export default config;
