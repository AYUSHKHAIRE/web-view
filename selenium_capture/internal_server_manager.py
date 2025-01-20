import asyncio
import websockets
import json
import threading
from logger_config import logger

'''
a server class that helps in connecting the websocket server .
'''
class WebSocketServer:
    '''
    inputs:
    --hostname : the host you want to publish .
    --port : the port number you start the server 
    
    algorithm : None
    
    returns : None
    '''
    def __init__(
        self, 
        host='localhost', 
        port=9000
    ):
        self.host = host
        self.port = port
        self.clients = set()
        self.active_sockets = {}

    '''
    A method to define a user by socket connection .
    
    inputs:
    --websocket : websocket connection object .
    
    algorithm : 
    adds a new request to the touple .
    
    returns: None
    '''
    async def register(
        self, 
        websocket
    ):
        self.clients.add(websocket)
        logger.debug(f"[ SERVER ] Client connected: {websocket.remote_address}")

    '''
    A method to remove a user and socket connection .
    
    inputs:
    --websocket : websocket connection object .
    
    algorithm : 
    removes an existing request from the touple .
    
    returns: None
    '''
    async def unregister(
        self, 
        websocket
    ):
        self.clients.remove(websocket)
        logger.warning(f"[ SERVER ] Client disconnected: {websocket.remote_address}")

    '''
    a method to handle the client .
    
    inputs:
    --websocket : websocket connection object .
    
    algorithm :
    wait for the registration of the client .
    iterate via each message .
    connects and register , and test messages .
    handle connection break .
    unregister the user in case .
    
    returns : None
    '''
    async def handle_client(
        self, 
        websocket
    ):
        await self.register(websocket)
        try:
            async for message in websocket:
                message = json.loads(message)
                if message["special"] == "register":
                    logger.info(f"[ SERVER ] Received message for registration")
                    user_id = message["user_id"]
                    self.active_sockets[user_id] = websocket
                    await self.send_message(
                        user_id=user_id,
                        message=f"server received registration "
                    )
                    await self.send_message(
                        user_id=user_id,
                        message=f"Hello client ! ",
                        type="hello"
                    )
                if message["special"] == "hello":
                    logger.info(f"[ SERVER ] Received hello message")
                    user_id = message["user_id"]
                    await self.send_message(
                        user_id=user_id,
                        message=f"hello client", 
                        type = "hello"
                    )
                
        except websockets.exceptions.ConnectionClosed as e:
            logger.error(f"[ SERVER ] Connection closed: {e}\n")
        finally:
            await self.unregister(websocket)

    '''
    a method to send the message .
    
    inputs:
    --user_id : the user who want to send the message .
    --message : a string message that user want to send .
    --type : define a type if it is special .
    
    algorithm:
    it takes the websocket from available ones by user id .
    make a format , dump in json . 
    send it to the websocket .
    handles connection closes .
    
    returns :None
    '''
    async def send_message(
        self, 
        user_id, 
        message,
        type = None
    ):
        websocket = self.active_sockets.get(user_id)
        if websocket:
            try:
                logger.debug(f"[ SERVER ] server is sending to the client.")
                message = {
                    'user_id':user_id,
                    'message':message,
                    'type':type
                }
                message = json.dumps(message)
                await websocket.send(message)
            except websockets.exceptions.ConnectionClosedError:
                logger.critical(f"[ SERVER ] Connection closed for user_id {user_id}.")
        else:
            logger.warning(f"[ SERVER ] No active WebSocket connection found for user_id {user_id}.")

    '''
    a method to start the service asynchromously .
    input:None
    
    algorithm:
    start a new event loop to create and read messages , 
    and runs infinitely .
    
    returns:None
    '''
    def start(self):
        async def main():
            logger.warning(f"[ SERVER ] Server starting on {self.host}:{self.port}")
            async with websockets.serve(
                self.handle_client, 
                self.host, 
                self.port
            ):
                await asyncio.Future()  # Run forever

        # Create a new event loop and run the server
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(main())
        
    '''
    a method to start process in thread .
    input : None
    
    algorithm:
    call start function in thread .
    
    returns: None
    '''
    def start_in_thread(self):
        thread = threading.Thread(target=self.start)
        thread.start()
        logger.warning("[ SERVER ] Server started in a new thread.")
