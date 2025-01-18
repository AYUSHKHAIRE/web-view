from selenium import webdriver
import time 
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager 
from selenium.webdriver.chrome.options import Options
import websockets
import asyncio
import json

class WebSocketClient:
    def __init__(self, uri, user_id):
        """
        Initializes the WebSocket client.

        :param uri: The WebSocket server URI (e.g., "ws://localhost:8000").
        :param user_id: The unique identifier for this client.
        """
        self.uri = uri
        self.user_id = user_id
        self.websocket = None

    async def connect(self):
        """Connect to the WebSocket server and register the client."""
        try:
            self.websocket = await websockets.connect(self.uri)
            print(f"Connected to server at {self.uri}")

            # Register the client with the server
            registration_message = json.dumps({"special": "register", "user_id": self.user_id})
            await self.websocket.send(registration_message)
            print(f"registration message {registration_message} was sent to the {self.user_id}")
            print(f"Registered as user_id: {self.user_id}")

            # Start listening for incoming messages
            await self.listen()
        except Exception as e:
            print(f"Failed to connect: {e}")

    async def send_message(self, message):
        if self.websocket:
            try:
                if isinstance(message, dict):
                    message = json.dumps(message)
                await self.websocket.send(message)
                print(f"Sent: {message}")
            except websockets.exceptions.ConnectionClosed as e:
                print(f"Failed to send message, connection closed: {e}")
            except Exception as e:
                print(f"Error sending message: {e}")
        else:
            print("WebSocket is not connected.")

    async def listen(self):
        try:
            async for message in self.websocket:
                if not self.last_sent_message or self.last_sent_message != message:
                    print(f"Received from server: {message}")
                    await self.send_message({
                        "special":None,
                        "message":"I am client .",
                        "user_id":user_id
                        }
                    )
                self.last_sent_message = message 
                
        except websockets.exceptions.ConnectionClosed as e:
            print(f"Connection closed: {e}")
        except Exception as e:
            print(f"Error during message listening: {e}")

    async def close(self):
        if self.websocket:
            await self.websocket.close()
            print("Connection closed.")
        else:
            print("WebSocket is not connected.")

async def setup_connection(uri):
    client = WebSocketClient(uri, user_id)
    await client.connect()
    await asyncio.sleep(600)
    await client.close()
    
def run_driver(driver,url):
    driver.get(url)
    driver.save_screenshot("screenshot.png")
    print(url)
    time.sleep(5)
    driver.quit()

print("starting the session")

# settings
user_id = 11111111
default_url = "https://google.com"
websocket_uri = "ws://localhost:9000"

chrome_options = Options()
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-dev-shm-usage")
driver = webdriver.Chrome(
    service = Service(
        ChromeDriverManager().install()
    ),
    options = chrome_options
)


print("setting up connection")
asyncio.run(setup_connection(websocket_uri))

print("setting up chrome")
run_driver(driver=driver,url=default_url)

# from multiprocessing import shared_memory

# shm = shared_memory.SharedMemory(name="shared_mem")

# data = bytes(shm.buf[:]).rstrip(b'\x00')  
# print(f"Data read from shared memory: {data.decode('utf-8')}")

# shm.close()