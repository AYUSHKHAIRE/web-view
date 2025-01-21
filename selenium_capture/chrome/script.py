import time
import asyncio
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from logger_config import logger
from client import WebSocketClient
from multiprocessing import shared_memory
import threading
import base64

# Global Settings
user_id = 1111
default_url = "https://x.com"
websocket_uri = "ws://localhost:9000"
shared_memory_block = None
driver = None

def setup_selenium_driver():
    """Setup and return a Selenium WebDriver instance."""
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()), options=chrome_options
    )
    driver.set_window_size(1920,1080)
    return driver

   
def write_to_shared_memory(data):
    shm = shared_memory.SharedMemory(name=f'shared_memory_{user_id}', create=False)
    shm.buf[:] = bytearray(shm.size) 
    data_bytes = data.encode('utf-8')  
    if len(data_bytes) > shm.size:
        raise ValueError("Data size exceeds shared memory size")
    shm.buf[:len(data_bytes)] = data_bytes
    shm.buf[len(data_bytes)] = 0
    logger.info(f"wrote to sharedmemory successfully")
    shm.close()
    time.sleep(2)
        
def capture_and_write_screenshot(driver):
    driver.get(default_url)  # Ensure the driver navigates to the URL
    logger.info(f"got {default_url}")
    screenshot = driver.get_screenshot_as_base64()
    write_to_shared_memory(screenshot)
    time.sleep(2)
    logger.info("from thread")

def main():
    """Main function to run the client and Selenium driver."""
    logger.debug("[ CLIENT ] Starting WebSocket client...")
    ws_client = WebSocketClient(uri=websocket_uri, user_id=user_id)
    ws_client.start_in_thread()

    logger.debug("[ CLIENT ] Sending test message to WebSocket server...")
    ws_client.send_message_threadsafe(type="hello", message="Hello, server!")
    
    logger.debug("[ CLIENT ] writing the the shared memory ...")
    write_to_shared_memory("client writing to memory .")

    logger.debug("[ CLIENT ] Setting up Selenium WebDriver...")
    driver = setup_selenium_driver()
    
    if driver is None:
        logger.error("[ CLIENT ] WebDriver setup failed.")
        return

    # Keep the main thread alive
    try:
        capture_and_write_screenshot(driver=driver)
    except KeyboardInterrupt:
        logger.info("[ CLIENT ] Shutting down...")
        asyncio.run(ws_client.close())

if __name__ == "__main__":
    main()
