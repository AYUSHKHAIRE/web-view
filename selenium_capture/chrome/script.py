import time
import asyncio
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from logger_config import logger
from client import WebSocketClient
from multiprocessing import shared_memory

# Global Settings
user_id = 11111111
default_url = "https://google.com"
websocket_uri = "ws://localhost:9000"
shared_memory_block = None

def setup_selenium_driver():
    """Setup and return a Selenium WebDriver instance."""
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-dev-shm-usage")
    return webdriver.Chrome(
        service=Service(ChromeDriverManager().install()), options=chrome_options
    )


def capture_screenshot(driver, url, screenshot_path="screenshot.png"):
    """Open the URL in the driver and capture a screenshot."""
    logger.info(f"[ CLIENT ] Opening URL: {url}")
    driver.get(url)
    driver.save_screenshot(screenshot_path)
    logger.info(f"[ CLIENT ] Screenshot saved: {screenshot_path}")
    time.sleep(5)
    driver.quit()


def write_to_shared_memory(data):
    shm = shared_memory.SharedMemory(name=f'shared_memory_{user_id}', create=False, size=1000)
    data_bytes = data.encode('utf-8')  
    if len(data_bytes) > shm.size:
        raise ValueError("Data size exceeds shared memory size")
    shm.buf[:len(data_bytes)] = data_bytes
    shm.buf[len(data_bytes)] = 0
    shm.close()
    
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
    capture_screenshot(driver, url=default_url)

    # Keep the main thread alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("[ CLIENT ] Shutting down...")
        asyncio.run(ws_client.close())

if __name__ == "__main__":
    main()
