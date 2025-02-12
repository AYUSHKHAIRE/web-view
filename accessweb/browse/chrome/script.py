import time
import asyncio
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import MoveTargetOutOfBoundsException
from multiprocessing import shared_memory
import os
from threading import Thread
import json
import websockets
import asyncio
import time
from logger_config import logger
from threading import RLock

class WebSocketClient:
    def __init__(self, uri, user_id, auth_token):
        self.uri = uri
        self.user_id = user_id
        self.auth_token = auth_token  
        self.websocket = None
        self.loop = asyncio.new_event_loop()
    
    def start_in_thread(self):
        """Start WebSocket client in a separate thread."""
        thread = Thread(target=self.run, daemon=True)
        thread.start()

    def run(self):
        """Run the event loop in a separate thread."""
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self.connect())

    async def connect(self):
        """Establish WebSocket connection with authentication."""
        try:
            headers = {
                'Origin':"http://127.0.0.1:8000",
                "Authorization": f"Bearer {self.auth_token}"
            }
            logger.debug(f"trying to connect to {self.uri}")
            self.websocket = await websockets.connect(self.uri, additional_headers=headers)
            logger.info(f"[ CLIENT ] Connected to server at {self.uri} with authentication.")

            # Send registration message
            await self.send_message(type="register", message="registerr request")
            logger.info(f"[ CLIENT ] Sent registration message for user_id: {self.user_id}")

            # Start listening for server messages
            await self.listen()
        except Exception as e:
            logger.error(f"[ CLIENT ] Connection error: {e}")

    async def send_message(self, type, message):
        """Send a message over WebSocket."""
        if self.websocket:
            try:
                message_payload = {
                    "special": type,
                    "user_id": self.user_id,
                    "message": message,
                }
                await self.websocket.send(json.dumps(message_payload))
                logger.info(f"[ CLIENT ] Sent message: {len(message_payload)}")
            except Exception as e:
                logger.error(f"[ CLIENT ] Error sending message: {e}")
        else:
            logger.warning("[ CLIENT ] WebSocket is not connected.")

    async def listen(self):
        """Listen for messages from the server."""
        try:
            async for message in self.websocket:
                logger.info(f"[ CLIENT ] Received message: {len(message)}")
                await self.handle_message(message)
        except Exception as e:
            logger.error(f"[ CLIENT ] Listening error: {e}")

    async def handle_message(self, message):
        """Handle incoming WebSocket messages."""
        logger.warning(f'{message}')
        data = json.loads(message)
        if data.get("type") == "register":
            logger.info(f"[ CLIENT ] Registration successful for user_id: {self.user_id}")
            # Send hello message
            await self.send_message(type="hello", message="Hello, server!")
        if data.get("type") == "click_on_driver":
            logger.info(f"[ CLIENT ] click request for user_id: {self.user_id}")
            logger.warning(data)
            SM.triggerbridge(type="click_on_driver",message=data)
            logger.warning("[ CLIENT ] click complete .")
        elif data.get("type") == "hello":
            logger.info(f"[ CLIENT ] Server says: {data['message']}")

    async def close(self):
        """Close the WebSocket connection."""
        if self.websocket:
            await self.websocket.close()
            logger.info("[ CLIENT ] WebSocket connection closed.")

    def send_message_threadsafe(self, type, message):
        """Send a message from outside the WebSocket's event loop."""
        if self.loop.is_running():
            asyncio.run_coroutine_threadsafe(
                self.send_message(type=type, message=message), self.loop
            )
        else:
            logger.warning("[ CLIENT ] WebSocket event loop is not running.")

class selenium_manager:
    def __init__(self):
        self.driver = None
        self.driver_lock = RLock()
        self.driver_instruction = None
        self.driver_message = None
        
    def setup_selenium_driver(self):
        """Setup and return a Selenium WebDriver instance."""
        start_time = time.time()
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.set_capability("goog:loggingPrefs", {"browser": "ALL"})
        main_driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()), options=chrome_options
        )
        outer_width = main_driver.execute_script("return window.outerWidth;")
        inner_width = main_driver.execute_script("return window.innerWidth;")
        outer_height = main_driver.execute_script("return window.outerHeight;")
        inner_height = main_driver.execute_script("return window.innerHeight;")
        width_diff = outer_width - inner_width
        height_diff = outer_height-inner_height
        n_screen_width = screen_width + width_diff
        n_screen_height = screen_height + height_diff
        main_driver.set_window_size(n_screen_width, n_screen_height)
        end_time = time.time()
        logger.info(f"[ SETUP ] Selenium WebDriver setup took {end_time - start_time:.4f} seconds")
        self.driver =  main_driver
  
    def triggerbridge(self,type, message):
        if type == "click_on_driver":
            try:
                logger.debug("trying to set up click onn driver")
                self.driver_message = "click_on_driver"
                self.driver_instruction = message
                logger.debug("set up click onn driver . hhanding over tto tread")
    
            except  Exception as e:
                logger.error(f"Error in clicking driver: {e}")
            
    def click_on_driver(self,driver,x, y):
        logger.warning("starting clickinng process")
        logger.warning("locked .")
        if driver:
            outer_width = driver.execute_script("return window.outerWidth;")
            inner_width = driver.execute_script("return window.innerWidth;")
            outer_height = driver.execute_script("return window.outerHeight;")
            inner_height = driver.execute_script("return window.innerHeight;")
            body_width = driver.execute_script("return document.body.scrollWidth;")
            body_height = driver.execute_script("return document.body.scrollHeight;")
            logger.info('Original x and y:', x, y)
            logger.info('Outer Dimensions:', outer_width, outer_height)
            logger.info('Inner Dimensions:', inner_width, inner_height)
            logger.info('Body Width:', body_width, 'Body Height:', body_height)
            new_y = y
            if y > inner_height:
                driver.execute_script(f"window.scrollTo(0, {y});")
            current_scroll_position = driver.execute_script("return window.pageYOffset;")
            new_y = y - current_scroll_position
            logger.info('Adjusted Y after scrolling:', new_y)
            element = driver.execute_script("return document.elementFromPoint(arguments[0], arguments[1]);", x, new_y)
            if element:
                try:
                    action = ActionChains(driver)
                    action.move_to_element(element).click().perform()
                    logger.debug(f'Clicked on element at {x}, {new_y}')
                    return driver
                except MoveTargetOutOfBoundsException:
                    logger.error(f'Failed to click at {x}, {new_y} due to out of bounds error')
            else:
                logger.warning(f'Element not found at {x}, {new_y}')
                return driver
        else:
            logger.error("Error in clicking driver")
                
    def write_to_shared_memory(self,screen_data,audio_data):
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
            # logger.info(f"Successfully wrote string data to shared memory for user {user_id} ({len(encoded_data_screen)} | {len(encoded_data_audio)} bytes)")
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

    def hit_url_on_browser(self):
        """Navigate WebDriver to a URL."""
        start_time = time.time()
        self.driver.get(default_url)
        end_time = time.time()
        logger.info(f"[ NAVIGATION ] Browser navigated to {default_url} in {end_time - start_time:.4f} seconds")

    def prepare_browser_for_audio(self):
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
            self.driver.execute_script(script)
            logger.warning("Script executed successfully in the browser")
        except Exception as e:
            logger.error(f"Error executing script in the browser: {e}")
        

    def clear_and_track_log(self):
        logs = self.driver.get_log('browser')  # Capture browser logs
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
                    frequency_data_string =  frequency_data_string.replace('[', '').replace(']', '')
                    fullstring += frequency_data_string
                except Exception as e:
                    logger.error(f"Error parsing frequency data: {e}")
        self.driver.execute_script('console.clear();')
        return fullstring 

    def capture_and_write_screenshot_and_audio(self):
        self.prepare_browser_for_audio()
        while True:
            try:
                start_time = time.time()
                if self.driver != None:
                    screenshot = self.driver.get_screenshot_as_base64()
                    audio = self.clear_and_track_log()
                    self.write_to_shared_memory(screenshot,audio)
                    logger.warning("looking for operators")
                    if self.driver_instruction and self.driver_message:
                        logger.warning("operator cracked")
                        logger.warning(f"prinnting values {self.driver_instruction} and {self.driver_message}")
                        logger.debug("listenning to innsttructtion")
                        logger.warning(f'{type(self.driver_instruction)}')
                        logger.warning(f'{type(self.driver_message)}')
                        if self.driver_message == "click_on_driver":
                            x = int(float(self.driver_instruction['x']))
                            y = int(float(self.driver_instruction['y']))
                            self.driver = self.click_on_driver(driver = self.driver,x = x ,y = y )
                            logger.debug("click operation complete")
                            self.driver_instruction = None
                            self.driver_message = None
                        logger.debug("wrapping up click")
                    logger.warning("operator bypass")
                else:
                    logger.error("driver is None")
                end_time = time.time()
                # logger.info(f"[ SCREENSHOT ] Captured and wrote screenshot in {end_time - start_time:.4f} seconds")
            except Exception as e:
                logger.error(f"Error capturing screenshot: {e}")
                break

# Environment variables
user_id = os.environ.get('CONTAINER_USER_ID')
auth_token = os.environ.get('CONTAINER_USER_AUTH_TOKEN')
screendex = os.environ.get('SCREENDEX')

screendex = screendex.replace('px', '')
screen_width = int(float(screendex.split('X')[0]))
screen_height = int(float(screendex.split('X')[1]))
logger.warning(f"got screen {screen_width} {screen_height}")

logger.debug(f"Starting Docker for user: {user_id}")

default_url = "https://www.youtube.com/watch?v=RFDeV3k2lsA"
websocket_uri = f"ws://127.0.0.1:8000/ws/browse/{user_id}/"

SM = selenium_manager()

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
    
    SM.write_to_shared_memory("Client writing to shared memory.","Client writing to shared memory.")

    logger.debug("[ CLIENT ] Setting up Selenium WebDriver...")
    SM.setup_selenium_driver()

    if SM.driver is None:
        logger.error("[ CLIENT ] WebDriver setup failed.")
        return

    SM.hit_url_on_browser()

    try:
        screenshot_thread = Thread(target=SM.capture_and_write_screenshot_and_audio,daemon=True)
        screenshot_thread.start()
        # Keep the main thread alive
        while True:
            time.sleep(0.01)

    except KeyboardInterrupt:
        logger.info("[ CLIENT ] Shutting down...")
    finally:
        asyncio.run(ws_client.close())


if __name__ == "__main__":
    start_time = time.time()
    main()
    end_time = time.time()
    logger.info(f"[ TOTAL ] Entire script runtime: {end_time - start_time:.4f} seconds")