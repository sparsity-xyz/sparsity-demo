from abc import ABC, abstractmethod
from typing import List, Tuple

from cometbft.abci.v1 import types_pb2


HexString = str


class ApplicationInterface(ABC):
    @abstractmethod
    def init(self, initial_data: str):
        pass

    @abstractmethod
    def step(self, messages) -> List[types_pb2.Event]:
        pass

    @abstractmethod
    def status(self) -> Tuple[bool, HexString]:
        pass

    @abstractmethod
    def update(self, block_height: int):
        pass

class BaseApplication(ApplicationInterface):
    block_height: int

    def __init__(self):
        pass

    def init(self, initial_data: str):
        """Initialize with data from contract"""
        pass  # Don't return anything

    def step(self, messages) -> List[types_pb2.Event]:
        """Process messages"""
        # Return list of events in format:
        # [{'type': 'event_type', 'attributes': [{'key': 'k', 'value': 'v', 'index': True}]}]
        return []

    def status(self) -> Tuple[bool, HexString]:
        """Return end state and result"""
        return False, ""

    def update(self, block_height: int):
        """Update state with new block height"""
        self.block_height = block_height
