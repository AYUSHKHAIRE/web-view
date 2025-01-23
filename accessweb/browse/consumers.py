# chat/consumers.py
import json
from browse.logger_config import logger
from channels.generic.websocket import AsyncWebsocketConsumer

class WebSocketConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["user_id"]
        self.room_group_name = f"browse_{self.room_name}"

        # Add the channel to the group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()
        logger.debug(f"Connected to WebSocket room: {self.room_group_name}")

    async def disconnect(self, close_code):
        # Remove the channel from the group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        logger.debug(f"Disconnected from WebSocket room: {self.room_group_name}")

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            message_type = data.get("special")
            user_id = data.get("user_id", "unknown")

            if message_type == "register":
                # Handle registration
                response = {
                    "type": "register",
                    "message": f"Registered {user_id}"
                }
                logger.debug(f"Registered user {user_id}")
            elif message_type == "hello":
                # Handle a hello message
                response = {
                    "type": "hello",
                    "message": "Hello from server!"
                }
                logger.debug(f"Saying hello to user {user_id}")
            else:
                # Handle unknown message type
                response = {
                    "type": "error",
                    "message": "Unknown message type."
                }
                logger.warning(f"Unknown message type from user {user_id}")

            # Send the response back to the client
            await self.send(text_data=json.dumps(response))

        except json.JSONDecodeError:
            # Handle invalid JSON
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
