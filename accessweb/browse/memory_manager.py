from multiprocessing import shared_memory
from browse.logger_config import logger
class memoryManager:
    def __init__(self):
        self.shared_memory_pool = {} 
        
    def setup_memory(self, user_id):
        self.clean_memory(user_id)
        shm = shared_memory.SharedMemory(
            create=True, 
            size=6221440,  
            name=f"shared_memory_{user_id}"
        )
        self.shared_memory_pool[f'shared_memory_{user_id}'] = shm
        logger.debug(f"[ MEMORY ] Shared memory for user_id {user_id} is set up.")

    def read_memory(self, user_id):
        try:
            shm = shared_memory.SharedMemory(name=f'shared_memory_{user_id}', create=False)
            buffer = shm.buf.tobytes()  
            null_index = len(buffer) - 1
            while null_index >= 0 and buffer[null_index] == 0:
                null_index -= 1

            # Truncate at the null terminator
            buffer = buffer[:null_index + 1]  # +1 because index is zero-based
            if null_index != -1:
                buffer = buffer[:null_index]  # Truncate at the null terminator
            shm.close()
            logger.debug(f"[ MEMORY ] Binary data read from shared memory for user_id {user_id}.{len(buffer)}")
            return buffer

        except FileNotFoundError:
            logger.error(f"[ MEMORY ] Shared memory block for user_id {user_id} not found.")
            return None
        except Exception as e:
            logger.error(f"[ MEMORY ] Failed to read from shared memory for user_id {user_id}: {e}")
            return None

    def clean_memory(self,user_id):
        try:
            # Connect to the existing shared memory
            shm = shared_memory.SharedMemory(name=f"shared_memory_{user_id}")
            # Unlink (delete) the shared memory
            shm.unlink()
            logger.warning(f"Shared memory /shared_memory_{user_id} removed successfully.")
        except FileNotFoundError:
            logger.error(f"Shared memory /shared_memory_{user_id} not found.")