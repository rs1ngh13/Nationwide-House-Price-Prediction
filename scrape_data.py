from bs4 import BeautifulSoup

def extract_zillow_details(html):
    soup = BeautifulSoup(html, 'html.parser')
    data = {}

    #gather price
    price = soup.select_one("span.price-text")
    if not price:
        price = soup.select_one('span[data-testid="price"]')
    data["price"] = price.text.strip() if price else None

    #gather address data (specifically city, state, zipcode)
    address_tag = soup.select_one('h1.Text-c11n-8-109-3__sc-aiai24-0')
    if not address_tag:
        address_tag = soup.select_one('h1.Text-c11n-8-111-0__sc-aiai24-0')
    if address_tag:
        full_address = address_tag.text.strip()
        parts = full_address.split(",")
        if len(parts) >= 2:
            city_state_zip = parts[-1].strip()
            if len(parts) >= 3:
                city = parts[-2].strip()
                data["address"] = f"{city}, {city_state_zip}"
            else:
                data["address"] = city_state_zip
        else:
            data["address"] = full_address
    else:
        data["address"] = None


    #bed, bathroom, squarefoot data
    bbs = {}
    bbs_containers = soup.select('[data-testid="bed-bath-sqft-fact-container"]')
    for container in bbs_containers:
        text = container.get_text(separator=" ").lower()
        if "bed" in text:
            bbs["beds"] = text.strip()
        elif "bath" in text:
            bbs["baths"] = text.strip()
        elif "sqft" in text:
            bbs["sqft"] = text.strip()
    data.update(bbs)

    #at a glance information 
    at_glance = soup.select('[data-testid="at-a-glance"] span')
    if not at_glance:
        at_glance = soup.select('div[aria-label="At a glance facts"] span')
    data["at_a_glance"] = [x.text.strip() for x in at_glance if x.text.strip()]

    #facts and feature section
    facts = soup.select('[data-testid="fact-category"] span.Text-c11n-8-109-3__sc-aiai24-0')
    if not facts:
        facts = soup.select('div[data-testid="fact-category"] span')
    data["facts_features"] = [f.text.strip() for f in facts if f.text.strip()]

    #school ratings
    school_data = []
    school_section = soup.find("h5", string=lambda t: t and "GreatSchools rating" in t)
    if school_section:
        school_list = school_section.find_next("ul")
        if school_list:
            for li in school_list.find_all("li", recursive=False):
                spans = li.find_all("span")
                ratings = [s.text.strip() for s in spans if s.text.strip()]
                if len(ratings) >= 3:
                    school_data.append({ 
                        "school_level": ratings[2],
                        "rating": ratings[0]
                    })
    data["school_ratings"] = school_data
    return data


