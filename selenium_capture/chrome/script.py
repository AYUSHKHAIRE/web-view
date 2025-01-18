from selenium import webdriver
import time 
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager 
from selenium.webdriver.chrome.options import Options

chrome_options = Options()
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(
    service = Service(
        ChromeDriverManager().install()
    ),
    options = chrome_options
)

default_url = "https://google.com"

driver.get(default_url)
driver.save_screenshot("screenshot.png")

print(default_url)
# driver.scree
# time.sleep(15)
# driver.quit()
# from multiprocessing import shared_memory

# shm = shared_memory.SharedMemory(name="shared_mem")

# data = bytes(shm.buf[:]).rstrip(b'\x00')  
# print(f"Data read from shared memory: {data.decode('utf-8')}")

# shm.close()