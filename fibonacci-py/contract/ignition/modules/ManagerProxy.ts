import { buildModule } from "@nomicfoundation/hardhat-ignition/modules";
import * as dotenv from "dotenv";

dotenv.config();

const managerProxyModule = buildModule("ManagerProxyModule", (m) => {
    const proxyAdminOwner = m.getAccount(0);
    const contractOwner = m.getAccount(1);
    const manager = m.contract("Manager");

    const encodedFunctionCall = m.encodeFunctionCall(manager, "initialize", [
        contractOwner,
    ]);

    // init with owner
    const proxy = m.contract("TransparentUpgradeableProxy", [
        manager,
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

const managerModule = buildModule("ManagerModule", (m) => {
    const { proxy, proxyAdmin } = m.useModule(managerProxyModule);

    const manager = m.contractAt("Manager", proxy);

    return { manager, proxy, proxyAdmin };
});


export default managerModule;
