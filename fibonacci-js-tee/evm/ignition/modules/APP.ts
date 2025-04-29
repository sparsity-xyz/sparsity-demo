import { buildModule } from "@nomicfoundation/hardhat-ignition/modules";
import * as dotenv from "dotenv";

dotenv.config();

const appModule = buildModule("appModule", (m) => {
    const outpostAddress = process.env.OUTPOST_PROXY_CONTRACT || "";
    const app = m.contract("APP", [outpostAddress]);

    return { app };
});

export default appModule;
