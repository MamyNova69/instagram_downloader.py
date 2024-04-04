from selenium import webdriver
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def ouvrir_session_chrome():
	chrome_options = webdriver.ChromeOptions()
	# chrome_options.add_argument('--ignore-certificate-errors')
	# chrome_options.add_argument('--allow-insecure-localhost')
	# chrome_options.add_argument('--disable-web-security')
	# chrome_options.add_argument("--headless")
	chrome_options.add_argument("--mute-audio")
	# chrome_options.add_argument("--remote-debugging-port=12345") # select a port
	# chrome_options.add_argument('--incognito')
	chrome_options.add_argument("start-maximized")
	chrome_options.add_argument('--log-level=3')
	chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
	chrome_options.add_argument("--disable-blink-features=AutomationControlled")
	chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"]) 
	chrome_options.add_experimental_option("useAutomationExtension", False)
	path_to_extension = r"ublock/uBlock-Origin.crx"
	chrome_options.add_extension(path_to_extension)
	global driver
	driver = webdriver.Remote("http://172.25.0.5:4444", options=chrome_options)
	driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})") 
	global wait
	wait = WebDriverWait(driver, 10)

def fermer_session_chrome():
	driver.quit()

def refresh():
	driver.refresh()

def open_newtab(url):
	driver.switch_to.new_window('tab')
	get_url(url)

def test():
	ouvrir_session_chrome()
	get_url("https://adblock-tester.com/")
	time.sleep(2)
	driver.save_screenshot("addtest1.png")
	get_url("https://adblock-tester.com/")
	time.sleep(2)
	driver.save_screenshot("addtest2.png")
	fermer_session_chrome()

def insert_JS():
	JS_get_network_requests = "var performance = window.performance || window.msPerformance || window.webkitPerformance || {}; var network = performance.getEntries() || {}; return network;"
	global network_requests
	network_requests = driver.execute_script(JS_get_network_requests)

def display_network_requests():
	for n in network_requests:
		url = n["name"]
		# print(url)
		# print only js file
		if ".js" in url:
			print(url)

def get_url(url):
	driver.get(url)
	insert_JS()
	wait.until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
	display_network_requests()


if __name__ == "__main__":
    test()

