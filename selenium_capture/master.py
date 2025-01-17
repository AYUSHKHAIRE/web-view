from browser_manager import browserManager
from memory_manager import memoryManager
from sessionmanager import sessionManager
from innternalServerManager import internalServerManager
import time

# Initialize managers
print("Initializing managers...")
BM = browserManager()
MM = memoryManager()
SSM = sessionManager()
SVM = internalServerManager()

# User ID for testing
user_id = '11111111'

# Call setup functions and print their status
time.sleep(0.1)
SSM.setup_docker(user_id=user_id)

time.sleep(0.1)
MM.setup_memory(user_id=user_id)

time.sleep(0.1)
MM.test_memory(user_id=user_id)

time.sleep(0.1)
BM.start_driver(user_id=user_id)

print("adding a new client")
time.sleep(0.1)
SVM.add_a_new_client(user_id=user_id)
