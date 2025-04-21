import { buildModule } from "@nomicfoundation/hardhat-ignition/modules";
import * as dotenv from "dotenv";

dotenv.config();

const outPostProxyModule = buildModule("OutpostProxyModule", (m) => {
    const proxyAdminOwner = m.getAccount(0);
    const contractOwner = m.getAccount(1);
    const outpost = m.contract("Outpost");

    const encodedFunctionCall = m.encodeFunctionCall(outpost, "initialize", [
        contractOwner,
    ]);

    // init with owner
    const proxy = m.contract("TransparentUpgradeableProxy", [
        outpost,
        proxyAdminOwner,
        encodedFunctionCall,
    ]);

    const proxyAdminAddress = m.readEventArgument(
        proxy,
        "AdminChanged",
        "newAdmin"
    );

    const proxyAdmin = m.contractAt("ProxyAdmin", proxyAdminAddress);

    return { proxyAdmin, proxy };
});

const outpostModule = buildModule("OutpostModule", (m) => {
    const { proxy, proxyAdmin } = m.useModule(outPostProxyModule);

    const outpost = m.contractAt("Outpost", proxy);

    return { outpost, proxy, proxyAdmin };
});

export default outpostModule;
