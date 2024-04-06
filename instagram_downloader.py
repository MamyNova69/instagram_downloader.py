import requests
import modules.navigateur_local_chrome as nav
# change to this, if you are using a remote server
# import modules.navigateur as nav
from browser_cookie3 import firefox
import time
from bs4 import BeautifulSoup
import re
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import os
from selenium.webdriver.support import expected_conditions as EC



instagram_url = "https://www.instagram.com/"
instagram_cookie_url =".instagram.com"

profil_page_link = "https://www.instagram.com/natgeo/"

img_pattern = r'src="(https:\/\/scontent.cdninstagram.com\/v\/.*?)"'
count_image = 0
IMG_URLS = []


def import_cookie() :
    cookies = firefox()
    filtered_cookies = [cookie for cookie in cookies if instagram_cookie_url in cookie.domain]
    chrome_cookies = [{
                    'domain': cookie.domain,
                    'include Subdomains': True,
                    'path': '/',
                    'Secure': True, 
                    'expirationDate': cookie.expires ,
                    'name': cookie.name, 
                    'value': cookie.value
                    }
                    for cookie in filtered_cookies]
    return chrome_cookies


def find_links_of_images():
    html = nav.driver.page_source
    links = re.findall(img_pattern, html)
    links = [url.replace('&amp;', '&') for url in links]
    # print(len(img_urls))
    return links
    


# Give a list to this function and it will download the images if they are not already downloaded
def download_images():
    global count_image
    count_image += 1
    folder_path = "images"
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    
    img_urls = find_links_of_images()
    # print(f"il y a {len(img_urls)} images sur la page")

    for each in img_urls:
        if each not in IMG_URLS:
            IMG_URLS.append(each)
            response = requests.get(each)
            time.sleep(0.1) # let's see if this helps
            if response.status_code == 200:
                count_image += 1
                with open(f"{folder_path}/image_{count_image}.jpg", "wb") as f:
                    f.write(response.content)
                    # print(f"Image {count_image} saved successfully")
            else:
                print(f"Failed to download image {count_image}")



if __name__ == "__main__":


    #open a session with chrome and login with your cookies
    chrome_cookies = import_cookie()
    nav.ouvrir_session_chrome()
    nav.get_url(instagram_url)

    for cookie in chrome_cookies:
        nav.driver.add_cookie(cookie)
    nav.get_url(instagram_url)
    nav.driver.save_screenshot("instagram.png")
    nav.get_url(profil_page_link)
    time.sleep(1)
    nav.driver.save_screenshot("instagram.png")


    img_urls = find_links_of_images()

    html = nav.driver.find_element(By.TAG_NAME, 'html')
    html.send_keys(Keys.END)
    
    x = len(find_links_of_images())
    while x < len(img_urls):
        time.sleep(0.1)
        x = len(find_links_of_images())



    # nav.driver.save_screenshot("instagram.png")


    download_images()

    publications = nav.driver.find_elements(By.XPATH, '//div[@style="display: flex; flex-direction: column; padding-bottom: 0px; padding-top: 0px; position: relative;"]')
    # print(len(publications))


    # normalement une seule balise, mais par souci de generalité on fait une boucle
    LINKS = []
    for publication in publications:
        links = publication.find_elements(By.TAG_NAME, 'a')
        for link in links:
            LINKS.append(link)

    # print(len(LINKS))

    # for link in LINKS:
    #     print(link.get_attribute('href'))



    for link in LINKS:
        time.sleep(1)
        link.click()
        box = nav.wait.until(EC.presence_of_element_located((By.XPATH, '//img[@style="object-fit: cover;"]')))

        download_images()

        suivant = nav.driver.find_elements(By.XPATH, '//button[@aria-label="Suivant"]')

        download_images()

        count_button = len(suivant)
        if count_button > 1:
            while count_button > 1:
                suivant = nav.driver.find_elements(By.XPATH, '//button[@aria-label="Suivant"]')
                try :
                    suivant[1].click()
                    download_images()
                except :
                    # print("pas d'image suivante")
                    break
                time.sleep(0.5)
                count_button = len(suivant)
                # print(count_button)

        else:
            pass
            # print("pas d'image suivante")

        htlm = nav.driver.find_element(By.TAG_NAME, 'html')
        htlm.send_keys(Keys.ESCAPE)











