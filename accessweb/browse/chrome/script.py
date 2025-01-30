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
screendex = os.environ.get('SCREENDEX')

screendex = screendex.replace('px', '')
screen_width = int(float(screendex.split('X')[0]))
screen_height = int(float(screendex.split('X')[1]))
logger.warning(f"got screen {screen_width} {screen_height}")

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
    outer_width = driver.execute_script("return window.outerWidth;")
    inner_width = driver.execute_script("return window.innerWidth;")
    outer_height = driver.execute_script("return window.outerHeight;")
    inner_height = driver.execute_script("return window.innerHeight;")
    width_diff = outer_width - inner_width
    height_diff = outer_height-inner_height
    n_screen_width = screen_width + width_diff
    n_screen_height = screen_height + height_diff
    driver.set_window_size(n_screen_width, n_screen_height)
    end_time = time.time()
    logger.info(f"[ SETUP ] Selenium WebDriver setup took {end_time - start_time:.4f} seconds")
    return driver

def write_to_shared_memory(screen_data,audio_data):
    start_time = time.time()
    try:
        shms = shared_memory.SharedMemory(name=f"shared_memory_screen_{user_id}", create=False)
        shma = shared_memory.SharedMemory(name=f"shared_memory_audio_{user_id}", create=False)
        if not isinstance(screen_data, str):
            raise ValueError("Input data must be a string.")
        if not isinstance(audio_data, str):
            raise ValueError("Input data must be a string.")
        encoded_data_screen = screen_data.encode('utf-8')
        encoded_data_audio = audio_data.encode('utf-8')
        if len(encoded_data_screen) > shms.size:
            raise ValueError(f"Data size exceeds shared memory size: {len(encoded_data_screen)} / {shms.size}")
        if len(encoded_data_audio) > shma.size:
            raise ValueError(f"Data size exceeds shared memory size: {len(encoded_data_audio)} / {shma.size}")
        shms.buf[:len(encoded_data_screen)] = encoded_data_screen
        shms.buf[len(encoded_data_screen):] = b'\x00' * (shms.size - len(encoded_data_screen))
        shma.buf[:len(encoded_data_audio)] = encoded_data_audio
        shma.buf[len(encoded_data_audio):] = b'\x00' * (shma.size - len(encoded_data_audio))
        logger.info(f"Successfully wrote string data to shared memory for user {user_id} ({len(encoded_data_screen)} | {len(encoded_data_audio)} bytes)")
    except Exception as e:
        logger.error(f"Failed to write to shared memory for user {user_id}: {e}")
    finally:
        if 'shma' in locals() and 'shms' in locals():
            try:
                shms.close()
                shma.close()
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

def prepare_browser_for_audio(driver):
    """Capture a screenshot and write to shared memory."""
    logger.warning("Starting audio tracking script with execjs")
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
    

def clear_and_track_log(driver):
    logs = driver.get_log('browser')  # Capture browser logs
    fullstring = '' 
    for log in logs:
        message = log['message']
        if "Array(" in message :
            # Extract the array string part from the log message
            try:
                # Extract the array part of the message, which is formatted like `Array(512): [ ... ]`
                start_index = message.find('[')
                end_index = message.find(']')
                frequency_data_string = message[start_index:end_index+1]
                fullstring += frequency_data_string
            except Exception as e:
                logger.error(f"Error parsing frequency data: {e}")
    driver.execute_script('console.clear();')
    return fullstring 

def capture_and_write_screenshot_and_audio(driver):
    prepare_browser_for_audio(driver)
    while True:
        try:
            start_time = time.time()
            screenshot = driver.get_screenshot_as_base64()
            audio = clear_and_track_log(driver)
            write_to_shared_memory(screenshot,audio)
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
    write_to_shared_memory("Client writing to shared memory.","Client writing to shared memory.")

    logger.debug("[ CLIENT ] Setting up Selenium WebDriver...")
    driver = setup_selenium_driver()

    if driver is None:
        logger.error("[ CLIENT ] WebDriver setup failed.")
        return

    hit_url_on_browser(driver)

    try:
        screenshot_thread = Thread(target=capture_and_write_screenshot_and_audio, args=(driver, ), daemon=True)
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