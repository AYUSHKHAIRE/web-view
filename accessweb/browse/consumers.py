# chat/consumers.py
import json
from browse.logger_config import logger
from channels.generic.websocket import AsyncWebsocketConsumer
from browse.memory_manager import memoryManager
from browse.views import MM
import asyncio

class WebSocketConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["user_id"]
        self.room_group_name = f"browse_{self.room_name}"
        self.streaming = False  # Initially not streaming

        # Add the channel to the group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()
        logger.debug(f"Connected to WebSocket room: {self.room_group_name}")

    async def disconnect(self, close_code):
        self.streaming = False  # Stop streaming when the WebSocket disconnects

        # Remove the channel from the group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        logger.debug(f"Disconnected from WebSocket room: {self.room_group_name}")

    async def receive(self, text_data=None, bytes_data=None):
        try:
            if bytes_data:
                logger.debug(f"Received bytes data from user {self.room_name}")
                response = {
                    "type": "info",
                    "message": "Binary data received successfully."
                }
            elif text_data:
                data = json.loads(text_data)
                message_type = data.get("special")
                user_id = data.get("user_id", "unknown")
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
                elif message_type == "start_stream":
                    if not self.streaming:
                        self.streaming = True
                        asyncio.create_task(self.read_and_stream_screen())
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
            await self.send(text_data=json.dumps(error_response))

    async def send_to_group(self, event):
        # Broadcast a message to the group
        message = event["message"]
        await self.send(text_data=json.dumps(message))

    async def read_and_stream_screen(self):
        while self.streaming:
            try:
                memory_data = MM.read_memory(user_id=self.room_name)
                if memory_data:
                    await self.send(bytes_data=memory_data)
                    logger.debug(f"Sent image bytes to user {self.room_name},{len(memory_data)}")
                else:
                    logger.warning(f"No image data found for user {self.room_name}")
                await asyncio.sleep(0.01)

            except Exception as e:
                logger.error(f"Error in read_and_stream_screen: {e}")
                self.streaming = False
                break
