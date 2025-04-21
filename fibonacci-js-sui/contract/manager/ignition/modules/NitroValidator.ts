import { buildModule } from "@nomicfoundation/hardhat-ignition/modules";
import * as dotenv from "dotenv";

dotenv.config();

const NitroValidatorModule = buildModule("NitroValidatorModule", (m) => {
  const certManager = process.env.CERT_CONTRACT || "";
  if (!certManager) {
    throw new Error("CERT_CONTRACT environment variable is not set");
  }

  const nitroValidator = m.contract("NitroValidator", [certManager]);

  return { nitroValidator };
});

export default NitroValidatorModule;