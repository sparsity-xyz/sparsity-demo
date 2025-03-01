import { buildModule } from "@nomicfoundation/hardhat-ignition/modules";


const mockOutpostModule = buildModule("MockOutpostModule", (m) => {
    const outpost = m.contract("MockOutpost");

    return { outpost };
});

export default mockOutpostModule;
