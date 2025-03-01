import hashlib
import os
from typing import List
from cometbft.abci.v1 import types_pb2  # Use the correct protobuf types
import websocket_pb2 as websocket
import logging

logger = logging.getLogger(__name__)

class ConsensusState:

    def __init__(self, app):
        self.end = False
        self.last_block_height = 0
        self.last_app_hash = b'\x00' * 32
        initial_data = os.environ.get("INIT_DATA", "")
        self.app = app
        self.app.init(initial_data)

    def reset(self):
        self.end = False
        self.last_block_height = 0
        self.last_app_hash = b'\x00' * 32

    def step(self, raw_message) -> List[types_pb2.Event]:
        """
        Process a transaction and return events.
        
        Args:
            raw_message: The raw message bytes
            
        Returns:
            List[types_pb2.Event]: The events generated by processing the message
        """
        try:
            logger.info(f"Processing message of size {len(raw_message)} bytes")
            
            # Try to decode the message using the application's step method
            events = self.app.step(raw_message)
            
            # Log the events
            logger.info(f"Generated {len(events)} events")
            for i, event in enumerate(events):
                logger.info(f"Event {i+1}: type={event.type}, attributes={len(event.attributes)}")
            
            return events
        except Exception as e:
            logger.error(f"Error in step: {str(e)}")
            return []

    @staticmethod
    def decode_messages(raw_messages):
        print(f"Decoding messages: {raw_messages}")
        batch_message = websocket.BatchMessage()
        batch_message.ParseFromString(raw_messages)
        return batch_message.messages

    def update(self, block_height):
        self.app.update(block_height)
        self.last_block_height = block_height
        self.last_app_hash = hashlib.sha256(str(block_height).encode()).digest()
        return self.last_app_hash

    def status(self):
        return self.app.status()

    def close(self):
        self.end = True
