from logger_config import logger
from threading import Thread
import json
import websockets
import asyncio

class WebSocketClient:
    def __init__(self, uri, user_id):
        self.uri = uri
        self.user_id = user_id
        self.websocket = None
        self.loop = asyncio.new_event_loop()

    def start_in_thread(self):
        """Start WebSocket client in a separate thread."""
        thread = Thread(target=self.run, daemon=True)
        thread.start()

    def run(self):
        """Run the event loop in a separate thread."""
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self.connect())

    async def connect(self):
        """Establish WebSocket connection and handle communication."""
        try:
            self.websocket = await websockets.connect(self.uri)
            logger.info(f"[ CLIENT ] Connected to server at {self.uri}")

            # Send registration message
            await self.send_message(type="register", message=None)
            logger.info(f"[ CLIENT ] Sent registration message for user_id: {self.user_id}")

            # Start listening for server messages
            await self.listen()
        except Exception as e:
            logger.error(f"[ CLIENT ] Connection error: {e}")

    async def send_message(self, type, message):
        """Send a message over WebSocket."""
        if self.websocket:
            try:
                message_payload = {
                    "special": type,
                    "user_id": self.user_id,
                    "message": message,
                }
                await self.websocket.send(json.dumps(message_payload))
                logger.info(f"[ CLIENT ] Sent message: {message_payload}")
            except Exception as e:
                logger.error(f"[ CLIENT ] Error sending message: {e}")
        else:
            logger.warning("[ CLIENT ] WebSocket is not connected.")

    async def listen(self):
        """Listen for messages from the server."""
        try:
            async for message in self.websocket:
                logger.info(f"[ CLIENT ] Received message: {message}")
                await self.handle_message(message)
        except Exception as e:
            logger.error(f"[ CLIENT ] Listening error: {e}")

    async def handle_message(self, message):
        """Handle incoming WebSocket messages."""
        data = json.loads(message)
        if data.get("type") == "register":
            logger.info(f"[ CLIENT ] Registration successful for user_id: {self.user_id}")
            # Send hello message
            await self.send_message(type="hello", message="Hello, server!")
        elif data.get("type") == "hello":
            logger.info(f"[ CLIENT ] Server says: {data['message']}")

    async def close(self):
        """Close the WebSocket connection."""
        if self.websocket:
            await self.websocket.close()
            logger.info("[ CLIENT ] WebSocket connection closed.")

    def send_message_threadsafe(self, type, message):
        """Send a message from outside the WebSocket's event loop."""
        if self.loop.is_running():
            asyncio.run_coroutine_threadsafe(
                self.send_message(type=type, message=message), self.loop
            )
        else:
            logger.warning("[ CLIENT ] WebSocket event loop is not running.")

