import { buildModule } from "@nomicfoundation/hardhat-ignition/modules";

const managerUpgradeModule = buildModule("ManagerUpgradeModule", (m) => {
    const proxyAdminOwner = m.getAccount(0);
    const proxyAdminAddress = process.env.MANAGER_PROXY_ADMIN_CONTRACT || '';
    const proxyAddress = process.env.MANAGER_PROXY_CONTRACT || '';
    const proxyAdmin = m.contractAt("ProxyAdmin", proxyAdminAddress);
    const proxy = m.contractAt("TransparentUpgradeableProxy", proxyAddress);
    const newManager = m.contract("Manager");
  
    // const encodedFunctionCall = m.encodeFunctionCall(newManager, "initialize", [
    // ]);
  
    m.call(proxyAdmin, "upgradeAndCall", [proxy, newManager, "0x"], {
      from: proxyAdminOwner,
    });
  
    return { proxyAdmin, proxy };
});

export default managerUpgradeModule;
