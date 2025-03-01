from eth_abi.abi import decode, encode

from base_app import BaseApplication, HexString


class Fibonacci(BaseApplication):
    def __init__(self):
        self.result = 0

    def init(self, initial_data: str):
        if initial_data:
            try:
                # Remove '0x' prefix if it exists, otherwise use as-is
                hex_data = initial_data[2:] if initial_data.startswith('0x') else initial_data
                decoded = decode(['uint256'], bytes.fromhex(hex_data))
                self.result = self.fibonacci(int(decoded[0]))
                print(f'Fibonacci result: {self.result}')
                print(f'Fibonacci result settlement data: {self.get_result_data()}')
            except Exception as e:
                print(f"Error decoding initial data: {e}")
                self.result = 0
        else:
            # it can be empty string if no initial data sent by contract
            self.result = 1
            print("no initial data")

    def status(self):
        """Return end state and result"""
        return self.result != 0, self.get_result_data()

    @staticmethod
    def fibonacci(n: int) -> int:
        if n <= 1:
            return n
        return Fibonacci.fibonacci(n - 1) + Fibonacci.fibonacci(n - 2)

    def get_result(self):
        return self.result

    def get_result_data(self) -> HexString:
        """Return result encoded for blockchain"""
        # Add '0x' prefix to hex string
        return '0x' + encode(['uint256'], [self.result]).hex()


if __name__ == "__main__":
    from src.service import ABCIService
    import os

    os.environ['INIT_DATA'] = '0x000000000000000000000000000000000000000000000000000000000000001E' # 30
    ABCIService(Fibonacci()).start()