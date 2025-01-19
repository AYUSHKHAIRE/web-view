from multiprocessing import shared_memory
from logger_config import logger

class memoryManager:
    def __init__(self):
        self.shared_memory_pool = {} 
        
    def setup_memory(self,user_id):
        shm = shared_memory.SharedMemory(
            create=True, 
            size=128000, 
            name=f"sms_{user_id}"
        )
        self.shared_memory_pool[f'sms_{user_id}'] = shm
        logger.debug(f"[ MEMORY ] Shared memory for user_id {user_id} is set up.")
    
    def test_memory(self,user_id):
        data = b"Hello from host !!"
        self.shared_memory_pool[
            f'sms_{user_id}'
            ].buf[
                :len(data)] = data
        logger.debug(f"[ MEMORY ] host Data written to shared memory: {data.decode('utf-8')}")
        