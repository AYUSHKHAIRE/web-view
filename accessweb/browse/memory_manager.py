from multiprocessing import shared_memory
from browse.logger_config import logger
class memoryManager:
    def __init__(
        self
    ):
        self.shared_memory_pool = {} 
        
    def setup_memory(
        self, 
        user_id
    ):
        self.clean_memory(
            user_id
        )
        shms = shared_memory.SharedMemory(
            create=True, 
            size=6221440,  
            name=f"shared_memory_screen_{user_id}"
        )
        shma = shared_memory.SharedMemory(
            create=True, 
            size=6221440,  
            name=f"shared_memory_audio_{user_id}"
        )
        self.shared_memory_pool[f'shared_memory_screen_{user_id}'] = shms
        self.shared_memory_pool[f'shared_memory_audio_{user_id}'] = shma
        # logger.debug(f"[ MEMORY ] Shared memory for user_id {user_id} is set up.")

    def read_memory(
        self, 
        user_id
    ):
        try:
            # Attach to the shared memory block
            shms = shared_memory.SharedMemory(
                name=f'shared_memory_screen_{user_id}', 
                create=False
            )
            shma = shared_memory.SharedMemory(
                name=f'shared_memory_audio_{user_id}', 
                create=False
            )

            # Read only the non-zero portion of the buffer
            buffers = memoryview(
                shms.buf
                ).tobytes()  # Avoid creating unnecessary copies
            buffera = memoryview(
                shma.buf
                ).tobytes()  # Avoid creating unnecessary copies
            null_indexs = buffers.find(b'\x00')  # Locate the first null byte
            null_indexa = buffera.find(b'\x00')  # Locate the first null byte
            buffers = buffers[:null_indexs] if null_indexs != -1 else buffers  # Slice up to the first null byte
            buffera = buffera[:null_indexa] if null_indexa != -1 else buffera  # Slice up to the first null byte

            # Decode bytes to string
            datas = buffers.decode('utf-8')
            dataa = buffera.decode('utf-8')
            # logger.debug(f"[ MEMORY ] Data read from shared memory for user_id {user_id}. Size: {len(buffers)} | {len(buffera)} bytes")
            return datas,dataa
        except FileNotFoundError:
            logger.error(f"[ MEMORY ] Shared memory for user_id {user_id} not found.")
        except Exception as e:
            logger.error(f"[ MEMORY ] Failed to read from shared memory for user_id {user_id}: {e}")
        finally:
            try:
                if 'shms' in locals() and 'shma' in locals():  # Ensure `shm` is closed
                    shms.close()
                    shma.close()
            except Exception as e:
                logger.warning(f"[ MEMORY ] Failed to close shared memory for user_id {user_id}: {e}")

        return ""

    def clean_memory(
        self,
        user_id
    ):
        try:
            shm = shared_memory.SharedMemory(
                name=f'shared_memory_{user_id}', 
                create=False
            )
            shm.unlink()  # Unlink the shared memory
            logger.info(f"[ MEMORY ] Successfully unlinked shared memory for user_id {user_id}.")
        except FileNotFoundError:
            logger.warning(f"[ MEMORY ] Shared memory for user_id {user_id} not found during cleanup.")
        except Exception as e:
            logger.error(f"[ MEMORY ] Failed to unlink shared memory for user_id {user_id}: {e}")

    def shared_memory_exists(
        self,
        user_id
    ):
        try:
            logger.warning(f"Checking shared memory for user_id {user_id}.")
            screen_memory = f"shared_memory_screen_{user_id}"
            audio_memory = f"shared_memory_audio_{user_id}"
            shms = shared_memory.SharedMemory(
                name=screen_memory, 
                create=False
            )
            shma = shared_memory.SharedMemory(
                name=audio_memory, 
                create=False
            )
            shms.close()  # Close immediately if it exists
            shma.close()  # Close immediately if it exists
            logger.warning(f"[ MEMORY ] Shared memory for user_id {user_id} exists.")
            return True
        except FileNotFoundError:
            logger.error(f"[ MEMORY ] Shared memory for user_id {user_id} does not exist.")
            return False  # Shared memory does not exist
        except Exception as e:
            print(f"[ MEMORY ] Unexpected error while checking shared memory '{user_id}': {e}")
            return False  # Handle other errors safely
