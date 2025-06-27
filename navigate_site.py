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
    driver.maximize_window()
    return driver

#locate search bar and type city name with individual strokes
def search_city(driver, city_name):
    driver.get("https://www.zillow.com/")
    search_bar = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//input[@placeholder="Enter an address, neighborhood, city, or ZIP code"]'))
    )
    search_bar.clear()
    for char in city_name:
        search_bar.send_keys(char)
        time.sleep(random.uniform(0.1, 0.6))
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
        skip_button.click()
        time.sleep(1)
    except Exception:
        pass

#base urls
def urls(driver):
    current = driver.current_url.split("?")[0].rstrip("/")
    return current

#scroll to bottom of page to load all listings in html
def scroll_page(driver):
    try:
        container = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "search-page-list-container"))
        )
        for _ in range(8):
            driver.execute_script("arguments[0].scrollTop += 1000;", container)
            time.sleep(random.uniform(0.6, 1.2))
    except Exception:
        pass

def collect_listings(driver, base_url, num_pages=2):
    all_links = set()

    for page in range(1, num_pages+1):
        if page > 1:
            driver.get(f"{base_url}/{page}_p/")
            time.sleep(5)
        scroll_page(driver)

        try:
            tiles = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.XPATH, '//ul[contains(@class, "photo-cards")]/li'))
            )
        except Exception:
            continue

        for tile in tiles:
            for a in tile.find_elements(By.TAG_NAME, "a"):
                href = a.get_attribute("href")
                if href and "zillow.com/homedetails" in href:
                    all_links.add(href.split("?")[0])
    return list(all_links)

def extract_data(driver, links, city):
    listing_data = []
    for i, url in enumerate(links[:3]):
        try:
            driver.get(url)
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.TAG_NAME, "h1"))
            )
            time.sleep(random.uniform(2.5, 5))
            html = driver.page_source
            raw = extract_zillow_details(html)
            clean = extract_clean_features(
                raw.get("facts_features", []),
                raw.get("school_ratings", [])
            )
            record = {**raw, **clean, "city": city}
            listing_data.append(record)
        except Exception:
            continue
    return listing_data

def save_excel(data, filename="dataset.xlsx"):
    df = pd.DataFrame(data)
    df.drop(columns=["facts_features", "school_ratings", "url"], errors="ignore", inplace=True)
    df.to_excel(filename, index=False)
    print(f"Saved {len(df)} rows to {filename}")

def main():
    cities_df = pd.read_excel("city_names.xlsx")  
    all_data = []
    driver = initialize_browser()
    for city in cities_df["city_state"].dropna().unique():
        print(f"\n-----Scraping {city}-----")
        search_city(driver, city)
        deal_with_pop_up(driver)
        base = urls(driver)
        links = collect_listings(driver, base)
        print(f"  Found {len(links)} listing URLs")
        data = extract_data(driver, links, city)
        print(f"  Extracted {len(data)} records")
        all_data.extend(data)
    driver.quit()
    save_excel(all_data)

if __name__ == "__main__":
    main()
