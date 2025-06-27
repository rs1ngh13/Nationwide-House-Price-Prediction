import time
import random
import pandas as pd
from scrape_data import extract_zillow_details 
from filter_features import extract_clean_features
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from undetected_chromedriver import Chrome

def initialize_browser():
    driver = Chrome()
    driver.get("https://www.zillow.com/")
    return driver

#locate search bar and type city name with individual strokes
def search_city(driver, city_name):
    search_bar = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//input[@placeholder="Enter an address, neighborhood, city, or ZIP code"]'))
    )
    for char in city_name:
        search_bar.send_keys(char)
        time.sleep(0.1)
    search_bar.send_keys(Keys.RETURN)
    time.sleep(5)

#deal with pop-up if happens
def deal_with_pop_up(driver):
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
def urls(driver):
    current_url = driver.current_url.split("?")[0].rstrip('/')
    return current_url if not current_url.endswith("/") else current_url[:-1]


#scroll to bottom of page to load all listings in html
def scroll_page(driver):
    try:
        scroll_container = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "search-page-list-container"))
        )
        for _ in range(8):  
            driver.execute_script("arguments[0].scrollTop += 1000;", scroll_container)
            time.sleep(random.uniform(0.6, 1.2))

    except Exception as e:
        print("Scrolling failed", e)

def collect_listings(driver, base_url, num_pages=3):
    all_links = set()

    for page_num in range(1, num_pages + 1):
        if page_num > 1:
            page_url = f"{base_url}/{page_num}_p/"
            driver.get(page_url)
            print(f"Went to page {page_num}: {page_url}")
            time.sleep(5)

        scroll_page(driver)

        try:
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

        except Exception as e:
            print(f"Failed to get listings on page {page_num}: {e}")

    print(f"Total unique listings collected over {num_pages} pages: {len(all_links)}")
    return list(all_links)

def extract_data(driver, links):
    listing_data = []

    for i, url in enumerate(list(links)[:3]):  
        try:
            print(f"Listing {i+1}: {url}")
            driver.get(url)
            WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.TAG_NAME, "h1")))
            time.sleep(random.uniform(2.5, 5))

            html = driver.page_source
            raw_data = extract_zillow_details(html)

            cleaned_data = extract_clean_features(raw_data.get("facts_features", []), raw_data.get("school_ratings", []))
            final_data = {**raw_data, **cleaned_data}
            listing_data.append(final_data)  # collect for DataFrame
            print(f"Data for listing {i+1}:\n{final_data}\n")

        except Exception as e:
            print(f"Couldn't get data for listing {i+1}: {e}")

    return listing_data

def save_excel(data):
    df = pd.DataFrame(data)
    df.drop(columns=["facts_features", "school_ratings", "url"], errors="ignore", inplace=True)
    df.to_excel("dataset.xlsx", index=False)
    print("Data saved to file.")

def main():
    driver = initialize_browser()
    search_city(driver, "Stamford")
    deal_with_pop_up(driver)
    base_url = urls(driver)
    links = collect_listings(driver, base_url)
    data = extract_data(driver, links)
    driver.quit()
    save_excel(data)


if __name__ == "__main__":
    main()