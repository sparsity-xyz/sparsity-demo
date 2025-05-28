from nitro_toolkit.enclave.base_app import BaseNitroEnclaveApp
from fastapi import Request
from fastapi.responses import JSONResponse
import logging

logger = logging.getLogger("bank-app")

class BankApp(BaseNitroEnclaveApp):
    def __init__(self, vsock: bool = False, dns: bool = True):
        super().__init__(vsock=vsock, dns=dns)
        self.balances = {}

    def init_router(self):
        super().init_router()
        self.app.add_api_route("/deposit", self.deposit, methods=["POST"])
        self.app.add_api_route("/withdraw", self.withdraw, methods=["POST"])
        self.app.add_api_route("/transfer", self.transfer, methods=["POST"])

    async def deposit(self, request: Request):
        data = await request.json()
        address = data.get("address")
        amount = data.get("amount")
        signature = data.get("signature")
        if not address or not amount or not signature:
            return JSONResponse({"status": "error", "message": "Missing address, amount, or signature"}, status_code=400)
        # TODO: Verify signature here
        self.balances[address] = self.balances.get(address, 0) + int(amount)
        logger.info(f"Deposit: {amount} to {address} (sig={signature})")
        return JSONResponse({"status": "success", "event": "Deposit", "address": address, "amount": amount})

    async def withdraw(self, request: Request):
        data = await request.json()
        address = data.get("address")
        amount = data.get("amount")
        signature = data.get("signature")
        if not address or not amount or not signature:
            return JSONResponse({"status": "error", "message": "Missing address, amount, or signature"}, status_code=400)
        # TODO: Verify signature here
        if self.balances.get(address, 0) < int(amount):
            return JSONResponse({"status": "error", "message": "Insufficient balance"}, status_code=400)
        self.balances[address] -= int(amount)
        logger.info(f"Withdraw: {amount} from {address} (sig={signature})")
        return JSONResponse({"status": "success", "event": "Withdraw", "address": address, "amount": amount})

    async def transfer(self, request: Request):
        data = await request.json()
        from_address = data.get("from_address")
        to_address = data.get("to_address")
        amount = data.get("amount")
        if not from_address or not to_address or not amount:
            return JSONResponse({"status": "error", "message": "Missing from_address, to_address, or amount"}, status_code=400)
        if self.balances.get(from_address, 0) < int(amount):
            return JSONResponse({"status": "error", "message": "Insufficient balance"}, status_code=400)
        self.balances[from_address] -= int(amount)
        self.balances[to_address] = self.balances.get(to_address, 0) + int(amount)
        logger.info(f"Transfer: {amount} from {from_address} to {to_address}")
        return JSONResponse({"status": "success", "event": "Transfer", "from_address": from_address, "to_address": to_address, "amount": amount})

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--vsock", action="store_true", default=False)
    parser.add_argument("--dns", action="store_true", default=True)
    args = parser.parse_args()
    app = BankApp(vsock=args.vsock, dns=args.dns)
    app.run()
