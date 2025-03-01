from cometbft.abci.v1 import types_pb2 as types_pb2
from src.base_service import BaseABCIService
from src.consensus_state import ConsensusState
from src.base_app import BaseApplication
import logging

logger = logging.getLogger(__name__)


class ABCIService(BaseABCIService):
    def __init__(self, app: BaseApplication, port=26658):
        super().__init__(port)
        self.consensus_state = ConsensusState(app)

    def Info(self, request, context) -> types_pb2.InfoResponse:
        return types_pb2.InfoResponse(
            data='python abci application',
            version='0.0.1',
            app_version=1,
            last_block_height=self.consensus_state.last_block_height,
            last_block_app_hash=self.consensus_state.last_app_hash,
        )

    def InitChain(self, request, context) -> types_pb2.InitChainResponse:
        self.consensus_state.reset()
        return super().InitChain(request, context)

    def FinalizeBlock(self, request, context):
        """
        FinalizeBlock is called at the end of a block to finalize the block's transactions.
        """
        response = types_pb2.FinalizeBlockResponse()
        if self.consensus_state.end:
            return response
        
        try:
            tx_results = []
            all_events = []  # Collect all events
            
            # Process each transaction
            for tx in request.txs:
                # Process the transaction using the application's step method
                logger.info(f"Processing transaction of size {len(tx)} bytes")
                tx_events = self.consensus_state.step(tx)
                
                # Log the events
                logger.info(f"Transaction generated {len(tx_events)} events")
                
                # Add events to the collection
                if tx_events:
                    all_events.extend(tx_events)
                
                # Create a result for this transaction
                exec_tx_res = types_pb2.ExecTxResult()
                exec_tx_res.code = 0  # Success
                
                # Add any events specific to this transaction
                if tx_events:
                    for event in tx_events:
                        exec_tx_res.events.append(event)
                
                tx_results.append(exec_tx_res)
            
            # Create the response with all transaction results
            response = types_pb2.FinalizeBlockResponse(
                tx_results=tx_results
            )
            
            # Add all events to the response
            if all_events:
                for event in all_events:
                    response.events.append(event)
            
            # Check if the session has ended
            end, state_result = self.consensus_state.status()
            if end:
                logger.info(f"Session has ended, adding __end__ event with data: {state_result}")
                
                # Add an __end__ event to the response
                end_event = types_pb2.Event(
                    type='__end__',
                    attributes=[
                        types_pb2.EventAttribute(
                            key='data',
                            value=state_result,
                            index=True
                        )
                    ]
                )
                response.events.append(end_event)
                
                # Close the consensus state
                self.consensus_state.close()
            
            # Update the app hash
            response.app_hash = self.consensus_state.update(request.height)
            
            logger.info(f"FinalizeBlock response has {len(response.events)} events and {len(response.tx_results)} tx results")
            return response
        except Exception as e:
            logger.error(f"Error in FinalizeBlock: {str(e)}")
            # Return a response with error results
            tx_results = []
            for _ in request.txs:
                exec_tx_res = types_pb2.ExecTxResult()
                exec_tx_res.code = 1  # Error
                exec_tx_res.log = f"Error: {str(e)}"
                tx_results.append(exec_tx_res)
            
            return types_pb2.FinalizeBlockResponse(tx_results=tx_results)


if __name__ == "__main__":
    from src.base_app import BaseApplication
    import os

    # os.environ['INIT_DATA'] = '0x000000000000000000000000000000000000000000000000000000000000001E' # 30
    ABCIService(BaseApplication()).start()