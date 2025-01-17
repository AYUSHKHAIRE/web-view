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

print(default_url)
time.sleep(15)
driver.quit()