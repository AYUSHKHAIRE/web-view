# chat/consumers.py
import json
from browse.logger_config import logger
from channels.generic.websocket import AsyncWebsocketConsumer
from browse.memory_manager import memoryManager
from browse.views import MM
import asyncio
import time

class WebSocketConsumer(
    AsyncWebsocketConsumer
):
    async def connect(
        self
    ):
        self.room_name = self.scope["url_route"]["kwargs"]["user_id"]
        self.room_group_name = f"browse_{self.room_name}"
        self.streaming = False  # Initially not streaming

        # Add the channel to the group
        await self.channel_layer.group_add(
            self.room_group_name, 
            self.channel_name
        )
        await self.accept()
        logger.debug(f"Connected to WebSocket room: {self.room_group_name}")

    async def disconnect(
        self, 
        close_code
    ):
        self.streaming = False  # Stop streaming when the WebSocket disconnects
        # Remove the channel from the group
        await self.channel_layer.group_discard(
            self.room_group_name, 
            self.channel_name
        )
        logger.debug(f"Disconnected from WebSocket room: {self.room_group_name}")

    async def receive(
        self, 
        text_data=None, 
        bytes_data=None
    ):
        try:
            if text_data:
                data = json.loads(
                    text_data
                )
                # logger.warning(data)
                message_type = data.get("special")
                user_id = data.get(
                    "user_id", 
                    "unknown"
                )
                logger.warning(data)
                if message_type == "register":
                    response = {
                        "type": "register",
                        "message": f"Registered {user_id}"
                    }
                    logger.debug(f"Registered user {user_id}")
                elif message_type == "hello":
                    response = {
                        "type": "hello",
                        "message": "Hello from server!"
                    }
                    logger.debug(f"Saying hello to user {user_id}")
                elif message_type == "click_on_driver":
                    response = {
                        "type": "click_on_driver",
                        "x": data['message']['x'], 
                        "y":data['message']['y']
                    }
                    logger.debug(f"Saying click to user {user_id}")
                elif message_type == "search":
                    response = {
                        "type": "search",
                        "qurrey": data['querry']
                    }
                    logger.debug(f"Saying search to user {user_id}")
                elif message_type == "keypress":
                    response = {
                        "type": "keypress",
                        "key": data['message']['key']
                    }
                    logger.debug(f"Saying keypress to user {user_id}")
                elif message_type == "hover":
                    response = {
                        "type": "hover",
                        "x": data['message']['x'],
                        "y": data['message']['y']
                    }
                    logger.debug(f"Saying hover to user {user_id}")
                elif message_type == "page_source":
                    response = {
                        "type": "page_source"
                    }
                    logger.debug(f"Saying page source to user {user_id}")
                elif message_type == "LLM_ask_a_text":
                    logger.warning(data)
                    response = {
                        "type": "LLM_ask_a_text",
                        "message":data["message"]
                    }
                    logger.debug(f"Saying send message to LLM by user {user_id}")
                elif message_type == "LLM_response":
                    response = {
                        "type": "LLM_response",
                        "message":data["message"]
                    }
                    logger.debug(f"Saying response by LLM to user {user_id}")
                elif message_type == "vision_ask_a_vision":
                    response = {
                        "type": "vision_ask_a_vision",
                        "message":data["message"]
                    }
                    logger.debug(f"Saying send message to vision api by user {user_id}")
                elif message_type == "vision_response":
                    response = {
                        "type": "vision_response",
                        "message":data["message"]
                    }
                    logger.debug(f"Saying response by vision to user {user_id}")
                elif message_type == "start_stream":
                    if not self.streaming:
                        self.streaming = True
                        asyncio.create_task(
                            self.read_and_stream()
                        )
                        response = {
                            "type": "info",
                            "message": "Started streaming."
                        }
                        logger.debug(f"Started streaming for user {user_id}")
                    else:
                        response = {
                            "type": "warning",
                            "message": "Streaming is already in progress."
                        }
                elif message_type == "stop_stream":
                    self.streaming = False
                    response = {
                        "type": "info",
                        "message": "Stopped streaming."
                    }
                    logger.debug(f"Stopped streaming for user {user_id}")
                else:
                    response = {
                        "type": "error",
                        "message": "Unknown message type."
                    }
                    logger.warning(f"Unknown message type from user {user_id}")
            else:
                response = {
                    "type": "error",
                    "message": "No data received."
                }
                logger.warning("No data received in WebSocket message.")
            if response:
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        "type": "send_to_group",
                        "message": response,
                    }
                )
        except json.JSONDecodeError:
            error_response = {
                "type": "error",
                "message": "Invalid JSON format."
            }
            logger.error("Received invalid JSON format.")
            await self.send(
                text_data=json.dumps(
                    error_response
                )
            )

    async def send_to_group(
        self, 
        event
    ):
        # Broadcast a message to the group
        message = event["message"]
        await self.send(
            text_data=json.dumps(
                message
            )
        )

    async def read_and_stream(
        self
    ):
        while self.streaming:
            try:
                start_time = time.perf_counter()
                
                # Read from shared memory
                screen , audio = MM.read_memory(
                    user_id=self.room_name
                )
                read_time = time.perf_counter()
                
                if screen or audio :
                    data_to_send = {
                        'user_id': self.room_name,
                        'type': "i",
                        'screen':screen,
                        'audio':audio
                    }
                    
                    # Send data over WebSocket
                    await self.send(
                        json.dumps(
                            data_to_send
                        )
                    )
                    send_time = time.perf_counter()
                    
                    # logger.debug(
                    #     f"Sent image string to user {self.room_name}, "
                    # )
                else:
                    logger.warning(f"No image data found for user {self.room_name}")
                    flag = MM.shared_memory_exists(
                        user_id=self.room_name
                    )
                    if flag == False:
                        logger.warning(f"Shared memory not found for user {self.room_name}.")
                        logger.warning(f"setting memory again for user {self.room_name}.")
                        MM.setup_memory(
                            user_id=self.room_name
                        )
                
                # Sleep
                sleep_start = time.perf_counter()
                await asyncio.sleep(0.1)
                sleep_time = time.perf_counter()
                
                # logger.debug(
                #     f"Sleep time: {sleep_time - sleep_start:.4f}s. Total loop time: {sleep_time - start_time:.4f}s"
                # )

            except Exception as e:
                logger.error(f"Error in read_and_stream: {e}")
                self.streaming = False
                break
