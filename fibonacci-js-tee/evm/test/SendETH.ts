const { expect } = require("chai");
import { ethers } from "hardhat";
import dotenv from 'dotenv';
dotenv.config();

describe("Send eth", function () {
    it("Send eth to fleet settler", async function () {
        const [,_owner] = await ethers.getSigners();

        // Connect to localhost
        const provider = new ethers.JsonRpcProvider("http://127.0.0.1:8545");

        const owner = await _owner.connect(provider);

        const blockNumber = await provider.getBlockNumber();
        console.log("Current block number:", blockNumber);

        const tx = await owner.sendTransaction({
            to: process.env.FLEET_SETTLER_ADDRESS || "",
            value: ethers.parseEther("10.0") // amount of ETH to send
        });

        await tx.wait();

        console.log("Transaction hash:", tx.hash);


    });
});
