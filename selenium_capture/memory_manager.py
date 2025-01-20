from multiprocessing import shared_memory
from logger_config import logger

class memoryManager:
    def __init__(self):
        self.shared_memory_pool = {} 
        
    def setup_memory(self,user_id):
        shm = shared_memory.SharedMemory(
            create=True, 
            size=128000, 
            name=f"shared_memory_{user_id}"
        )
        self.shared_memory_pool[f'shared_memory_{user_id}'] = shm
        logger.debug(f"[ MEMORY ] Shared memory for user_id {user_id} is set up.")
    
    def read_memory(self, user_id):
        try:
            shm = shared_memory.SharedMemory(name=f'shared_memory_{user_id}', create=False)
            buffer = shm.buf.tobytes()  # Convert buffer to bytes
            null_index = buffer.find(b'\x00')  # Null terminator
            if null_index != -1:
                buffer = buffer[:null_index]  # Truncate at null terminator
            data = buffer.decode('utf-8')
            shm.close()
            logger.debug(f"[ MEMORY ] Data read from shared memory for user_id {user_id}: {data}")
            return data
        except FileNotFoundError:
            logger.error(f"[ MEMORY ] Shared memory block for user_id {user_id} not found.")
            return None
