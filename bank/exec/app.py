from nitro_toolkit.enclave.base_app import BaseNitroEnclaveApp
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from eth_account.messages import encode_defunct
from eth_account import Account
from starlette.middleware.sessions import SessionMiddleware
import os
import secrets
import logging

logger = logging.getLogger("bank-app")

class BankApp(BaseNitroEnclaveApp):
    def __init__(self, vsock: bool = False, dns: bool = True):
        super().__init__(vsock=vsock, dns=dns)
        # Add CORS and session middleware
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        self.app.add_middleware(SessionMiddleware, secret_key=os.urandom(24))
        # In-memory balances for demo
        self.balances = {
            "0x6b04692c6ac106b44cb6e2088cf06468fa4c259d": 1000.0
        }

    def get_current_user(self, request: Request):
        user = request.session.get("user")
        return user.lower() if user else None

    def init_router(self):
        super().init_router()
        self.app.add_api_route("/nonce", self.nonce, methods=["GET"])
        self.app.add_api_route("/login", self.login, methods=["POST"])
        self.app.add_api_route("/me", self.me, methods=["GET"])
        self.app.add_api_route("/balance", self.get_balance, methods=["GET"])
        self.app.add_api_route("/deposit", self.deposit, methods=["POST"])
        self.app.add_api_route("/withdraw", self.withdraw, methods=["POST"])
        self.app.add_api_route("/transfer", self.transfer, methods=["POST"])

    async def nonce(self, request: Request):
        nonce = secrets.token_hex(16)
        request.session["nonce"] = nonce
        return {"nonce": nonce}

    async def login(self, request: Request):
        # Debug: log cookies and session state
        logger.info(f"/login cookies: {request.cookies}")
        logger.info(f"/login session: {request.session.items()}")
        data = await request.json()
        address = data.get("address")
        signature = data.get("signature")
        nonce = request.session.get("nonce")
        logger.info(f"/login address: {address}")
        logger.info(f"/login signature: {signature}")
        logger.info(f"/login nonce: {nonce}")
        if not nonce:
            return JSONResponse({"success": False, "error": "No nonce in session. Please retry login."}, status_code=400)
        message = encode_defunct(text=nonce)
        try:
            recovered = Account.recover_message(message, signature=signature)
            logger.info(f"/login recovered: {recovered}")
            if recovered.lower() == address.lower():
                request.session["user"] = address
                request.session.pop("nonce", None)
                return {"success": True}
            else:
                return JSONResponse({"success": False, "error": "Signature mismatch"}, status_code=401)
        except Exception as e:
            logger.info(f"/login exception: {e}")
            return JSONResponse({"success": False, "error": str(e)}, status_code=400)

    async def me(self, request: Request):
        user = request.session.get("user")
        if user:
            return {"address": user}
        return JSONResponse({"address": None}, status_code=401)

    async def get_balance(self, request: Request):
        user = self.get_current_user(request)
        if not user:
            raise HTTPException(status_code=401, detail="Not authenticated")
        balance = self.balances.get(user, 0.0)
        return {"address": user, "balance": balance}

    async def deposit(self, request: Request):
        user = self.get_current_user(request)
        if not user:
            raise HTTPException(status_code=401, detail="Not authenticated")
        data = await request.json()
        amount = float(data.get("amount", 0))
        if amount <= 0:
            raise HTTPException(status_code=400, detail="Invalid amount")
        self.balances[user] = self.balances.get(user, 0.0) + amount
        return {"address": user, "balance": self.balances[user]}

    async def withdraw(self, request: Request):
        user = self.get_current_user(request)
        if not user:
            raise HTTPException(status_code=401, detail="Not authenticated")
        data = await request.json()
        amount = float(data.get("amount", 0))
        if amount <= 0:
            raise HTTPException(status_code=400, detail="Invalid amount")
        if self.balances.get(user, 0.0) < amount:
            raise HTTPException(status_code=400, detail="Insufficient balance")
        self.balances[user] -= amount
        return {"address": user, "balance": self.balances[user]}

    async def transfer(self, request: Request):
        user = self.get_current_user(request)
        if not user:
            raise HTTPException(status_code=401, detail="Not authenticated")
        data = await request.json()
        to_address = data.get("to", "").lower()
        amount = float(data.get("amount", 0))
        if not to_address or amount <= 0:
            raise HTTPException(status_code=400, detail="Invalid parameters")
        if self.balances.get(user, 0.0) < amount:
            raise HTTPException(status_code=400, detail="Insufficient balance")
        self.balances[user] -= amount
        self.balances[to_address] = self.balances.get(to_address, 0.0) + amount
        return {
            "from": user,
            "to": to_address,
            "from_balance": self.balances[user],
            "to_balance": self.balances[to_address]
        }

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--vsock", action="store_true", default=False)
    parser.add_argument("--dns", action="store_true", default=True)
    args = parser.parse_args()
    app = BankApp(vsock=args.vsock, dns=args.dns)
    app.run()