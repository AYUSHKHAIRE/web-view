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
            # Attach to the shared memory block
            shm = shared_memory.SharedMemory(name=f'shared_memory_{user_id}', create=False)

            # Read only the non-zero portion of the buffer
            buffer = memoryview(shm.buf).tobytes()  # Avoid creating unnecessary copies
            null_index = buffer.find(b'\x00')  # Locate the first null byte
            buffer = buffer[:null_index] if null_index != -1 else buffer  # Slice up to the first null byte

            # Decode bytes to string
            data = buffer.decode('utf-8')
            logger.debug(f"[ MEMORY ] Data read from shared memory for user_id {user_id}. Size: {len(buffer)} bytes")
            return data
        except FileNotFoundError:
            logger.error(f"[ MEMORY ] Shared memory for user_id {user_id} not found.")
        except Exception as e:
            logger.error(f"[ MEMORY ] Failed to read from shared memory for user_id {user_id}: {e}")
        finally:
            try:
                if 'shm' in locals():  # Ensure `shm` is closed
                    shm.close()
            except Exception as e:
                logger.warning(f"[ MEMORY ] Failed to close shared memory for user_id {user_id}: {e}")

        return ""

    def clean_memory(self,user_id):
        try:
            shm = shared_memory.SharedMemory(name=f'shared_memory_{user_id}', create=False)
            shm.unlink()  # Unlink the shared memory
            logger.info(f"[ MEMORY ] Successfully unlinked shared memory for user_id {user_id}.")
        except FileNotFoundError:
            logger.warning(f"[ MEMORY ] Shared memory for user_id {user_id} not found during cleanup.")
        except Exception as e:
            logger.error(f"[ MEMORY ] Failed to unlink shared memory for user_id {user_id}: {e}")
