import { expect } from "chai";
import { ignition, ethers } from "hardhat";


import managerModule from "../ignition/modules/ManagerProxy";
import outpostMoudle from "../ignition/modules/OutpostProxy";

describe("Proxy", function () {
    describe("Proxy interaction", async function () {
        it("Manager", async function () {
            const [, , otherAccount] = await ethers.getSigners();

            const { manager } = await ignition.deploy(managerModule);
            console.log("manager", await manager.getAddress());
            manager.interface.fragments.forEach(fragment => {
                if (fragment.type === 'event') {
                    const sig = ethers.id(fragment.format());
                    console.log(`${fragment.name} Signature: ${sig}`);
                  }
            })
        });
        it("Output", async function () {
            const [, , otherAccount] = await ethers.getSigners();

            const { outpost } = await ignition.deploy(outpostMoudle);
            console.log("outpost", await outpost.getAddress());
            outpost.interface.fragments.forEach(fragment => {
                if (fragment.type === 'event') {
                    const sig = ethers.id(fragment.format());
                    console.log(`${fragment.name} Signature: ${sig}`);
                  }
            })
        });
    });
});
