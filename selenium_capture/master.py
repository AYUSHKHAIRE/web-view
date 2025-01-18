from browser_manager import browserManager
from memory_manager import memoryManager
from sessionmanager import sessionManager
from internal_server_manager import WebSocketServer
import time

# Initialize managers
print("Initializing managers...")
BM = browserManager()
MM = memoryManager()
SSM = sessionManager()
WSS = WebSocketServer(port=9000)

user_id = '11111111'

# Setup and start WebSocket server
WSS.start_in_thread()

# Proceed with other setups
time.sleep(0.1)
SSM.setup_docker(user_id=user_id)

time.sleep(0.1)
MM.setup_memory(user_id=user_id)

time.sleep(0.1)
MM.test_memory(user_id=user_id)

print("Starting the driver...")
time.sleep(0.1)
BM.start_driver(user_id=user_id)
