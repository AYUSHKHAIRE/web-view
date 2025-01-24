import time
import asyncio
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from logger_config import logger
from client import WebSocketClient
from multiprocessing import shared_memory
import os
from threading import Thread

# Environment variables
user_id = os.environ.get('CONTAINER_USER_ID')
auth_token = os.environ.get('CONTAINER_USER_AUTH_TOKEN')

logger.debug(f"Starting Docker for user: {user_id}")

# Constants
default_url = "https://www.apple.com/ipad-pro/"
websocket_uri = f"ws://127.0.0.1:8000/ws/browse/{user_id}/"

def setup_selenium_driver():
    """Setup and return a Selenium WebDriver instance."""
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()), options=chrome_options
    )
    driver.set_window_size(1920, 1080)
    return driver

def write_to_shared_memory(data):
    try:
        shm = shared_memory.SharedMemory(name=f"shared_memory_{user_id}", create=False)
        if not isinstance(data, bytes):
            raise ValueError("Data must be in bytes format.")  
        if len(data) > shm.size:
            raise ValueError(f"Data size exceeds shared memory size / {len(data)}/{shm.size}")
        shm.buf[:len(data)] = data
        logger.info(f"Successfully wrote bytes data to shared memory for user {user_id} {len(data)}")
        shm.close()
    except FileNotFoundError:
        logger.error(f"Shared memory {shm.name} not found.")
    except Exception as e:
        logger.error(f"Failed to write to shared memory: {e}")

def hit_url_on_browser(driver):
    """Navigate WebDriver to a URL."""
    driver.get(default_url)
    logger.info(f"Browser navigated to {default_url}")

def capture_and_write_screenshot(driver, ws_client):
    """Capture a screenshot and write to shared memory."""
    while True:
        try:
            screenshot = driver.get_screenshot_as_png()
            write_to_shared_memory(screenshot)
            # time.sleep(0.1)
        except Exception as e:
            logger.error(f"Error capturing screenshot: {e}")
            break

def main():
    """Main function to run the client and Selenium driver."""
    logger.debug("[ CLIENT ] Starting WebSocket client...")
    ws_client = WebSocketClient(uri=websocket_uri, user_id=user_id, auth_token=auth_token)
    ws_client.start_in_thread()

    logger.debug("[ CLIENT ] Sending test message to WebSocket server...")
    ws_client.send_message_threadsafe(type="hello", message="Hello, server!")

    logger.debug("[ CLIENT ] Writing to shared memory...")
    write_to_shared_memory("Client writing to shared memory.")

    logger.debug("[ CLIENT ] Setting up Selenium WebDriver...")
    driver = setup_selenium_driver()

    if driver is None:
        logger.error("[ CLIENT ] WebDriver setup failed.")
        return

    hit_url_on_browser(driver)

    try:
        screenshot_thread = Thread(target=capture_and_write_screenshot, args=(driver, ws_client), daemon=True)
        screenshot_thread.start()

        # Keep the main thread alive
        while True:
            time.sleep(0.01)

    except KeyboardInterrupt:
        logger.info("[ CLIENT ] Shutting down...")
    finally:
        asyncio.run(ws_client.close())
        driver.quit()

if __name__ == "__main__":
    main()
