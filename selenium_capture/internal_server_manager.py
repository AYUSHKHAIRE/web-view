import asyncio
import websockets
import json
import threading

class WebSocketServer:
    def __init__(self, host='localhost', port=9000):
        self.host = host
        self.port = port
        self.clients = set()
        self.active_sockets = {}

    async def register(self, websocket):
        self.clients.add(websocket)
        print(f"Client connected: {websocket.remote_address}")

    async def unregister(self, websocket):
        self.clients.remove(websocket)
        print(f"Client disconnected: {websocket.remote_address}")

    async def handle_client(self, websocket):
        await self.register(websocket)
        try:
            async for message in websocket:
                print(f"Received: {message}")
                message = json.loads(message)
                if message["special"] == "register":
                    user_id = message["user_id"]
                    self.active_sockets[user_id] = websocket
                    await self.send_message(user_id=user_id,message=f"server received : {message}")
                if message["special"] == None:
                    user_id = message["user_id"]
                    await self.send_message(user_id=user_id,message=f"server received : {message}")
                
        except websockets.exceptions.ConnectionClosed as e:
            print(f"Connection closed: {e}")
        finally:
            await self.unregister(websocket)

    async def send_message(self, user_id, message):
        websocket = self.active_sockets.get(user_id)
        if websocket:
            try:
                print(f"server is sending to the client {message}.")
                await websocket.send(message)
            except websockets.exceptions.ConnectionClosedError:
                print(f"Connection closed for user_id {user_id}.")
        else:
            print(f"No active WebSocket connection found for user_id {user_id}.")

    def start(self):
        async def main():
            print(f"Server starting on {self.host}:{self.port}")
            async with websockets.serve(self.handle_client, self.host, self.port):
                await asyncio.Future()  # Run forever

        # Create a new event loop and run the server
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(main())
        
    def start_in_thread(self):
        thread = threading.Thread(target=self.start)
        thread.start()
        print("Server started in a new thread.")
