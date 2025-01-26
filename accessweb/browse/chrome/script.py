import time
import asyncio
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from logger_config import logger
from client import WebSocketClient
from multiprocessing import shared_memory
import os
from threading import Thread
import ast
import re

# Environment variables
user_id = os.environ.get('CONTAINER_USER_ID')
auth_token = os.environ.get('CONTAINER_USER_AUTH_TOKEN')

logger.debug(f"Starting Docker for user: {user_id}")

# Constants
default_url = "https://www.youtube.com/watch?v=RFDeV3k2lsA"
websocket_uri = f"ws://127.0.0.1:8000/ws/browse/{user_id}/"

def setup_selenium_driver():
    """Setup and return a Selenium WebDriver instance."""
    start_time = time.time()
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.set_capability("goog:loggingPrefs", {"browser": "ALL"})
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

def track_audio(driver):
    logger.warning("Starting audio tracking script with execjs")

    # JavaScript to capture audio data
    script = """
    const audioElement = document.querySelector('audio, video');
    if (audioElement) {
        const audioContext = new (window.AudioContext || window.webkitAudioContext)();
        const source = audioContext.createMediaElementSource(audioElement);
        const analyser = audioContext.createAnalyser();
        analyser.fftSize = 1024;
        const dataArray = new Uint8Array(analyser.frequencyBinCount);

        source.connect(analyser);
        analyser.connect(audioContext.destination);

        function logFrequencyData() {
            analyser.getByteFrequencyData(dataArray);
            // Logging the array as a string (JSON format)
            console.log('Array(' + dataArray.length + '): ' + JSON.stringify(Array.from(dataArray)));
            requestAnimationFrame(logFrequencyData);
        }
        logFrequencyData();
    } else {
        console.warn("No audio or video element found.");
    }
    """
    
    try:
        # Execute the script in the browser using Selenium
        driver.execute_script(script)
        logger.warning("Script executed successfully in the browser")
    except Exception as e:
        logger.error(f"Error executing script in the browser: {e}")
    
    # Retrieve console logs and parse the frequency data
    while True:
        try:
            logs = driver.get_log('browser')  # Capture browser logs
            for log in logs:
                message = log['message']
                logger.debug(message)
                if "Array(" in message and "JSON.stringify" in message:
                    # Extract the array string part from the log message
                    try:
                        # Extract the array part of the message, which is formatted like `Array(512): [ ... ]`
                        start_index = message.find('[')
                        end_index = message.find(']')
                        frequency_data_string = message[start_index:end_index+1]
                        
                        # Parse the string into a Python list
                        frequency_data = json.loads(frequency_data_string)
                        
                        # Output the first 10 values (or all data, depending on your need)
                        logger.debug(f"Frequency Data: {frequency_data[:10]}...")  # Debug log the first 10 values
                        print(frequency_data)  # Print or process the data
                    except Exception as e:
                        logger.error(f"Error parsing frequency data: {e}")
        except Exception as e:
            logger.error(f"Error in audio tracking: {e}")
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
        # screenshot_thread = Thread(target=capture_and_write_screenshot, args=(driver, ws_client), daemon=True)
        # screenshot_thread.start()
        audio_thread = Thread(target=track_audio, args=(driver,), daemon=True)
        audio_thread.start()
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
