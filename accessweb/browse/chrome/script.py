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
default_url = "https://tenor.com/search/playing-gifs"
websocket_uri = f"ws://127.0.0.1:8000/ws/browse/{user_id}/"

def setup_selenium_driver():
    """Setup and return a Selenium WebDriver instance."""
    start_time = time.time()
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()), options=chrome_options
    )
    driver.set_window_size(1920, 1080)
    end_time = time.time()
    logger.info(f"[ SETUP ] Selenium WebDriver setup took {end_time - start_time:.4f} seconds")
    return driver

def write_to_shared_memory(data):
    start_time = time.time()
    try:
        shm = shared_memory.SharedMemory(name=f"shared_memory_{user_id}", create=False)
        if not isinstance(data, str):
            raise ValueError("Input data must be a string.")
        encoded_data = data.encode('utf-8')
        if len(encoded_data) > shm.size:
            raise ValueError(f"Data size exceeds shared memory size: {len(encoded_data)} / {shm.size}")
        shm.buf[:len(encoded_data)] = encoded_data
        shm.buf[len(encoded_data):] = b'\x00' * (shm.size - len(encoded_data))
        logger.info(f"Successfully wrote string data to shared memory for user {user_id} ({len(encoded_data)} bytes)")
    except Exception as e:
        logger.error(f"Failed to write to shared memory for user {user_id}: {e}")
    finally:
        if 'shm' in locals():
            try:
                shm.close()
            except Exception as close_error:
                logger.warning(f"Failed to close shared memory for user {user_id}: {close_error}")
        end_time = time.time()
        logger.info(f"[ MEMORY ] Writing to shared memory took {end_time - start_time:.4f} seconds")

def hit_url_on_browser(driver):
    """Navigate WebDriver to a URL."""
    start_time = time.time()
    driver.get(default_url)
    end_time = time.time()
    logger.info(f"[ NAVIGATION ] Browser navigated to {default_url} in {end_time - start_time:.4f} seconds")

def capture_and_write_screenshot(driver, ws_client):
    """Capture a screenshot and write to shared memory."""
    while True:
        try:
            start_time = time.time()
            screenshot = driver.get_screenshot_as_base64()
            write_to_shared_memory(screenshot)
            end_time = time.time()
            logger.info(f"[ SCREENSHOT ] Captured and wrote screenshot in {end_time - start_time:.4f} seconds")
        except Exception as e:
            logger.error(f"Error capturing screenshot: {e}")
            break

def main():
    """Main function to run the client and Selenium driver."""
    logger.debug("[ CLIENT ] Starting WebSocket client...")
    client_start = time.time()
    ws_client = WebSocketClient(uri=websocket_uri, user_id=user_id, auth_token=auth_token)
    ws_client.start_in_thread()
    client_end = time.time()
    logger.info(f"[ CLIENT ] WebSocket client setup took {client_end - client_start:.4f} seconds")

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
    start_time = time.time()
    main()
    end_time = time.time()
    logger.info(f"[ TOTAL ] Entire script runtime: {end_time - start_time:.4f} seconds")
