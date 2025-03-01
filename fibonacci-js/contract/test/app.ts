const { expect } = require("chai");
import { ethers } from "hardhat";
import dotenv from 'dotenv';
dotenv.config();

describe("APP session settlement", function () {

    // write your own encoding logic
    function encodeData(): string {
        // const result: any = 8;
        // const data = ethers.AbiCoder.defaultAbiCoder().encode(["uint256"], [result]);
        // return data;
        const result = process.env.RESULT || "0x";
        console.log("result data", result);
        return result;
    }

    it("session settlement", async function () {
        const [,_owner] = await ethers.getSigners();

        // Connect to localhost
        const provider = new ethers.JsonRpcProvider("http://127.0.0.1:8545");

        const owner = await _owner.connect(provider);

        const blockNumber = await provider.getBlockNumber();
        console.log("Current block number:", blockNumber);

        const appContract = await ethers.getContractAt("APP", process.env.APP_CONTRACT || "", owner);
        const outpostContract = await ethers.getContractAt("MockOutpost", process.env.OUTPOST_PROXY_CONTRACT || "", owner);

        const appAddress = await appContract.getAddress();
        const mockOutpostAddress = await outpostContract.getAddress();
        console.log("appAddress:", appAddress);
        console.log("mockOutpostAddress:", mockOutpostAddress);

        const appOutpostContract = await appContract._outpostContract();
        expect(appOutpostContract).to.equal(mockOutpostAddress);

        // get the current sessionId
        var fibNum = process.env.NUM;
        var sessionId = await appContract.sessionNum(fibNum)
        
        var result = await appContract.getFibonacci(sessionId)
        expect(result).to.equal(0);

        // test settlement
        const data = encodeData();

        var tx = await outpostContract.settle(appAddress, sessionId, false, data);
        await tx.wait();
        console.log("settle success");

        // check the status
        const session = await appContract._sessions(sessionId);
        console.log("session status:", session.status);

        const statusFinished = 3;
        expect(statusFinished).to.equal(session.status);

        // check the result
        result = await appContract.getFibonacci(fibNum)
        console.log("result:", result);
    });
});
