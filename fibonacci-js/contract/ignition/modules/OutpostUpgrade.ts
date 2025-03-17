import { buildModule } from "@nomicfoundation/hardhat-ignition/modules";
import * as dotenv from "dotenv";

dotenv.config();

const outpostUpgradeModule = buildModule("OutpostUpgradeModule", (m) => {
    const proxyAdminOwner = m.getAccount(0);
    const proxyAdminAddress = process.env.OUTPOST_PROXY_ADMIN_CONTRACT || '';
    const proxyAddress = process.env.OUTPOST_PROXY_CONTRACT || '';
    const proxyAdmin = m.contractAt("ProxyAdmin", proxyAdminAddress);
    const proxy = m.contractAt("TransparentUpgradeableProxy", proxyAddress);
    const newOutpost = m.contract("Outpost");
  
    // const encodedFunctionCall = m.encodeFunctionCall(newManager, "initialize", [
    // ]);
  
    m.call(proxyAdmin, "upgradeAndCall", [proxy, newOutpost, "0x"], {
      from: proxyAdminOwner,
    });
  
    return { proxyAdmin, proxy };
});

export default outpostUpgradeModule;
