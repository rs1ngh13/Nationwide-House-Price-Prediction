import time
import random
from scrape_data import extract_zillow_details 
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from undetected_chromedriver import Chrome

#initialize browser and website
driver = Chrome()
driver.get("https://www.zillow.com/")

#locate search bar and type city name with individual strokes
search_bar = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.XPATH, '//input[@placeholder="Enter an address, neighborhood, city, or ZIP code"]'))
)
for char in "Norwalk":
    search_bar.send_keys(char)
    time.sleep(0.1)
search_bar.send_keys(Keys.RETURN)
time.sleep(5)

#deal with pop-up if happens
try:
    skip_button = WebDriverWait(driver, random.uniform(2.5, 5)).until(
        EC.element_to_be_clickable((By.XPATH, '//button[contains(text(), "Skip this question")]'))
    )
    driver.execute_script("arguments[0].scrollIntoView(true);", skip_button)
    time.sleep(0.5)
    driver.execute_script("arguments[0].click();", skip_button)
    print("got past pop up")
except Exception as e:
    print("you suck, give up", e)

#base url
current_url = driver.current_url.split("?")[0].rstrip('/')
base_url = current_url if not current_url.endswith("/") else current_url[:-1]

all_links = set()

#urls for the next pages, up to 3 pages
for page_num in range(1, 4):
    if page_num > 1:
        page_url = f"{base_url}/{page_num}_p/"
        driver.get(page_url)
        print(f"Went to page {page_num}: {page_url}")
        time.sleep(5)

    #scroll to bottom of page to load all listings in html
    for _ in range(5):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(random.uniform(2.5, 4.5))

    #locate tiles that are listings
    tiles = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.XPATH, '//ul[contains(@class, "photo-cards")]/li'))
    )
    print(f"Page {page_num}: Found {len(tiles)} listings.")

    for tile in tiles:
        try:
            links = tile.find_elements(By.TAG_NAME, 'a')
            for link in links:
                href = link.get_attribute("href")
                if href and "zillow.com/homedetails" in href:
                    all_links.add(href.split("?")[0])
        except:
            continue

print(f"Total unique listings collected over 3 pages: {len(all_links)}")

#extract data from listings
for i, url in enumerate(list(all_links)[:10]):  
    try:
        print(f"Listing {i+1}: {url}")
        driver.get(url)
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.TAG_NAME, "h1")))
        time.sleep(random.uniform(2.5, 5))

        html = driver.page_source
        data = extract_zillow_details(html)
        print(f"Data for listing {i+1}:\n{data}\n")

    except Exception as e:
        print(f"Couldn't get data for listing {i+1}: {e}")

driver.quit()
