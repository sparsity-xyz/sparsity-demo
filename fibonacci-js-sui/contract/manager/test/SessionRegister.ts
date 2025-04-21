const { expect } = require("chai");
import { ethers } from "hardhat";
import dotenv from 'dotenv';
dotenv.config();

describe("All contract", function () {
    it("Test new game", async function () {
        const [,_owner] = await ethers.getSigners();

        // Connect to localhost
        const provider = new ethers.JsonRpcProvider("http://127.0.0.1:8545");

        const owner = await _owner.connect(provider);

        const blockNumber = await provider.getBlockNumber();
        console.log("Current block number:", blockNumber);

        const outPostContract = await ethers.getContractAt("Outpost", process.env.OUTPOST_PROXY_CONTRACT || "", owner);
        const managerContract = await ethers.getContractAt("Manager", process.env.MANAGER_PROXY_CONTRACT || "", owner);
        const gameContract = await ethers.getContractAt("MiniGame", process.env.MINI_GAME_PROXY_CONTRACT || "", owner);

        const serviceAddress = await outPostContract.getAddress();
        const gameAddress = await gameContract.getAddress();
        const managerAddress = await managerContract.getAddress();

        console.log("service address", serviceAddress);
        console.log("game address", gameAddress);
        console.log("manager address", managerAddress);

        // register server to manager
        // check the chainId
        const network = await provider.getNetwork();
        var endpoint = "";
        // local node
        endpoint = "http://127.0.0.1:3001"
        const server = {
            endpoint: endpoint,
            publicKey: process.env.FLEET_SETTLER_ADDRESS || "",
        };

        const tx = await managerContract.registerSessions([server, server, server]);
        console.log("register Servers", await tx.wait());
    });
});
