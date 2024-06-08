import requests
import modules.navigateur_local_chrome as nav
from browser_cookie3 import firefox
import time
import re
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import os
from selenium.webdriver.support import expected_conditions as EC


profil_page_link = input("Enter the profile page link: ")
profile_name = re.search(r'instagram\.com/([^/]+)/?$', profil_page_link).group(1)


clean_profile_name = re.sub(r'[^a-zA-Z0-9_]', '', profile_name)
print(clean_profile_name)

# next input is not working yet
num_pictures = int(input("Enter the number of pictures you want to download: "))
date = time.strftime("%Y-%m-%d %H-%M-%S")


instagram_url = "https://www.instagram.com/"
instagram_cookie_url =".instagram.com"

# img_pattern = r'src="(https:\/\/scontent.cdninstagram.com\/v\/.*?)"'
img_pattern = r'src="(https:\/\/scontent-cdg4-2.cdninstagram.com\/v\/.*?)"'
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
    folder_path = f"images/{clean_profile_name}"
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
                global count_image
                count_image += 1
                with open(f"{folder_path}/{clean_profile_name}_{count_image}.jpg", "wb") as f:
                    f.write(response.content)
                    print(f"Image {count_image} saved successfully")
            else:
                print(f"Failed to download image")

def navigate(x, link):
    # navigate and download new images
    # x is the number of arrows to click to go to the next page
    time.sleep(1)
    link.click()
    box = nav.wait.until(EC.presence_of_element_located((By.XPATH, '//img[@style="object-fit: cover;"]')))
    download_images()
    suivant = nav.driver.find_elements(By.XPATH, '//button[@aria-label="Suivant"]')
    count_button = len(suivant)

    #adjust the number the number of arrows if the have a storries in profil that go to a next page
    if count_button > x:
        while count_button > x:
            suivant = nav.driver.find_elements(By.XPATH, '//button[@aria-label="Suivant"]')
            try :
                suivant[x].click()
                download_images()
            except :
                # print("pas d'image suivante")
                break
            time.sleep(0.5)
            count_button = len(suivant)
    else:
        pass
        # print("pas d'image suivante")

    htlm = nav.driver.find_element(By.TAG_NAME, 'html')
    htlm.send_keys(Keys.ESCAPE)



if __name__ == "__main__":


    chrome_cookies = import_cookie()
    nav.ouvrir_session_chrome()
    nav.get_url(instagram_url)

    for cookie in chrome_cookies:
        nav.driver.add_cookie(cookie)
    nav.get_url(instagram_url)

    nav.get_url(profil_page_link)
    time.sleep(1)

    img_urls = find_links_of_images()
    download_images()


    LINKS = {}
    # make it a dictionary with the href as key and link as value
    
    while count_image < num_pictures:

        # need to rethink this as links can contain multiple images
        # actually ok if I navigate and download after each publications links
        NEW_LINKS = {}

        xpath = "//div[contains(@style, 'display: flex; flex-direction: column;')]"
        publications = nav.driver.find_elements(By.XPATH, xpath)
        
        for publication in publications:
            links = publication.find_elements(By.TAG_NAME, 'a')

            for link in links:
                if link.get_attribute('href') not in LINKS:
                    LINKS[link.get_attribute('href')] = link
                    NEW_LINKS[link.get_attribute('href')] = link
        
        for link in NEW_LINKS.items() : # try with LINKS and NEW_LINKS
            suivant = nav.driver.find_elements(By.XPATH, '//button[@aria-label="Suivant"]')
            count_button = len(suivant)
            if count_button == 0:
                navigate(0, link[1])
            elif count_button == 1:
                navigate(1, link[1])
        
        img_urls = find_links_of_images()
        download_images()

        #scroll to the end of the page to load all the images
        html = nav.driver.find_element(By.TAG_NAME, 'html')
        html.send_keys(Keys.END)
        time.sleep(5) # find another solution to wait for the page to load
        
    print(f"Downloaded {count_image} images")
    nav.driver.quit()
    print("End of the program")


