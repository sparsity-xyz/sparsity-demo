import { buildModule } from "@nomicfoundation/hardhat-ignition/modules";
import * as dotenv from "dotenv";

dotenv.config();

// Module name needs to match to get the expected address 0x0E78D750EAE19Aa6C5211703DD33E13a5DE127e4
const certManagerModule = buildModule("certManagerModule", (m) => {
    const certManager = m.contract("CertManager");
    return { certManager };
});

export default certManagerModule;
