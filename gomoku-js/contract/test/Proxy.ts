import { expect } from "chai";
import { ignition, ethers } from "hardhat";

import managerModule from "../ignition/modules/ManagerProxy";
import outpostMoudle from "../ignition/modules/OutpostProxy";

describe("Proxy", function () {
    describe("Proxy interaction", async function () {
        it("Manager", async function () {
            const [, , otherAccount] = await ethers.getSigners();

            const { manager } = await ignition.deploy(managerModule);

            expect(await manager.connect(otherAccount).owner()).to.equal("0x70997970C51812dc3A010C7d01b50e0d17dc79C8");
        });
        it("Output", async function () {
            const [, , otherAccount] = await ethers.getSigners();

            const { outpost } = await ignition.deploy(outpostMoudle);

            expect(await outpost.connect(otherAccount).owner()).to.equal("0x70997970C51812dc3A010C7d01b50e0d17dc79C8");
        });
    });
});
