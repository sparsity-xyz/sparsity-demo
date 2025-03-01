from src.base_app import BaseApplication
from src.service import ABCIService
from autogen import ConversableAgent, config_list_from_json
import json
import logging
import os
from cometbft.abci.v1 import types_pb2
from typing import List
import hashlib
from websocket_pb2 import Message, BatchMessage

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AG2(BaseApplication):
    def __init__(self):
        """Initialize the AG2 ABCI application"""
        super().__init__()
        self.chat_history = []
        self.assistant = None
        self.fact_checker = None
        self.session_ended = False  # Track if session is ended
        self.setup_agents()
        self.initial_data = ""

    def setup_agents(self):
        """Setup AutoGen agents"""
        try:
            config_list = config_list_from_json(env_or_file=os.path.join(os.path.dirname(__file__), "../", "api_key.json"))
            llm_config = {"config_list": config_list}

            self.assistant = ConversableAgent(
                name="assistant",
                system_message="You are a helpful AI assistant that provides clear and concise responses.",
                llm_config=llm_config
            )

            self.fact_checker = ConversableAgent(
                name="fact_checker",
                system_message="You are a fact-checking assistant. Verify information and correct inaccuracies.",
                llm_config=llm_config
            )
            
            logger.info("Agents setup successfully")
        except Exception as e:
            logger.error(f"Failed to setup agents: {e}")
            raise

    def init(self, initial_data=""):
        """Initialize application state"""
        logger.info(f"Initializing AG2 with data: {initial_data}")
        self.initial_data = initial_data
        self.chat_history = []

    def step(self, messages) -> List[types_pb2.Event]:
        events = []
        logger.info(f"ABCI step called with message of size {len(messages)} bytes")
        
        try:
            # Decode the message
            
            # Try to parse as a BatchMessage first
            try:
                batch_message = BatchMessage()
                batch_message.ParseFromString(messages)
                
                # Process each message in the batch
                for message in batch_message.messages:
                    # Process the individual message
                    message_events = self._process_message(message)
                    if message_events:
                        events.extend(message_events)
            except Exception as batch_error:
                logger.info(f"Not a BatchMessage, trying as single Message: {str(batch_error)}")
                
                # Try to parse as a single Message
                try:
                    message = Message()
                    message.ParseFromString(messages)
                    
                    # Process the individual message
                    message_events = self._process_message(message)
                    if message_events:
                        events.extend(message_events)
                except Exception as message_error:
                    logger.error(f"Failed to parse as Message: {str(message_error)}")
                    
                    # Try as a JSON string
                    try:
                        content = json.loads(messages.decode('utf-8'))
                        logger.info(f"Decoded as JSON: {json.dumps(content, indent=2)}")
                        
                        # Process as a direct JSON message - handle both 'CHAT' and 'new' request types
                        if 'requestType' in content and content['requestType'] in ['CHAT', 'new']:
                            message_text = content.get('message', '')
                            logger.info(f"Chat message: '{message_text}'")
                            
                            # Process the chat message
                            chat_events = self._process_chat_message(message_text)
                            if chat_events:
                                events.extend(chat_events)
                    except Exception as json_error:
                        logger.error(f"Failed to parse as JSON: {str(json_error)}")
        except Exception as e:
            logger.error(f"Error in step: {str(e)}")
        
        logger.info(f"Returning {len(events)} events")
        return events

    def _process_message(self, message) -> List[types_pb2.Event]:
        """Process a single Message object"""
        events = []
        
        try:
            # Extract the data from the message
            if message.data:
                try:
                    # Try to decode as JSON
                    content = json.loads(message.data.decode('utf-8'))
                    logger.info(f"Decoded message data: {json.dumps(content, indent=2)}")
                    
                    # Check if it's a chat message - handle both 'CHAT' and 'new' request types
                    if content.get('requestType') in ['CHAT', 'new']:
                        message_text = content.get('message', '')
                        logger.info(f"Chat message: '{message_text}'")
                        
                        # Process the chat message
                        chat_events = self._process_chat_message(message_text)
                        if chat_events:
                            events.extend(chat_events)
                except Exception as e:
                    logger.error(f"Error decoding message data: {str(e)}")
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
        
        return events

    def _process_chat_message(self, message_text: str) -> List[types_pb2.Event]:
        """Process a chat message and return events"""
        events = []
        
        logger.info(f"Processing chat message: '{message_text}'")
        
        # Check if user wants to exit
        if message_text.lower() == "exit":
            logger.info("Exit command received, ending session")
            self.session_ended = True
            # Add a regular chat response for the exit command
            exit_event = types_pb2.Event(
                type='chat_response',
                attributes=[
                    types_pb2.EventAttribute(
                        key='response',
                        value=json.dumps({"messages": [{"agent": "system", "content": "Chat session ended, wait for the settlement", "role": "assistant"}]}),
                        index=True
                    )
                ]
            )
            logger.info(f"Created exit event: {exit_event}")
            events.append(exit_event)
            
            logger.info(f"Session ended, returning {len(events)} events")
            return events
        
        # Process chat with AutoGen agents
        logger.info("Processing with AutoGen agents")
        response = self.process_chat(message_text)
        logger.info(f"AutoGen response: {json.dumps(response, indent=2)}")
        
        # Create event with chat response
        chat_event = types_pb2.Event(
            type='chat_response',
            attributes=[
                types_pb2.EventAttribute(
                    key='response',
                    value=json.dumps(response),
                    index=True
                )
            ]
        )
        logger.info(f"Created chat_response event: {chat_event}")
        events.append(chat_event)
        logger.info("Created chat_response event")
        
        # Add to chat history
        self.chat_history.append({
            'message': message_text,
            'response': response
        })
        logger.info("Added to chat history")
        
        logger.info(f"Returning {len(events)} events from _process_chat_message")
        return events

    def status(self) -> tuple[bool, str]:
        """Return current status and chat history"""
        # Only return True if session is explicitly ended with "exit"
        return self.session_ended, self.get_result_data()

    def update(self, block_height):
        """Update state with new block height"""
        pass

    def format_chat_result(self, chat_result):
        """Format the chat result into a structured response"""
        if not chat_result or not hasattr(chat_result, 'chat_history'):
            return {"messages": []}
        
        formatted_messages = []
        for msg in chat_result.chat_history:
            formatted_messages.append({
                "agent": msg.get('name', 'unknown'),
                "content": msg.get('content', ''),
                "role": "assistant"
            })
        
        return {"messages": formatted_messages}

    def get_result_data(self):
        """Return hash of chat history for blockchain storage"""
        # Convert chat history to a JSON string
        chat_history_json = json.dumps(self.chat_history, sort_keys=True)
        
        # Create a hash of the chat history
        chat_hash = hashlib.sha256(chat_history_json.encode('utf-8')).hexdigest()
        
        # Return the hash prefixed with 0x to make it a valid hex string
        return f"0x{chat_hash}"

    def process_chat(self, message):
        """Process a chat message with AutoGen agents"""
        # Process chat with agents
        chat_result = self.assistant.initiate_chat(
            recipient=self.fact_checker,
            message=message,
            max_turns=1
        )

        # Format response
        response = self.format_chat_result(chat_result)
        
        return response

if __name__ == "__main__":
    # Create the AG2 application
    app = AG2()
    
    # Start the ABCI server in the main thread
    abci_server = ABCIService(app)
    abci_server.start()
