def extract_clean_features(facts_features: list, school_ratings: list) -> dict:

    #keywords that matter from the facts_feature list
    keywords = [
        "Hardwood Floor", "Skylight", "Balcony", "Central Air", "Laundry",
        "Open Floorplan", "Basement", "Attic", "Number of fireplaces",
        "Total structure area", "Total interior livable area",
        "Attached garage spaces", "Size", "Home type", "Architectural style",
        "Property subtype", "Year built", "Price per square foot",
        "Annual tax amount"
    ]

    cleaned_data = {}

    #loop through items in the facts_features
    for item in facts_features:
        item = item.strip()

        #takes care of key-value items
        if ":" in item:
            key, value = item.split(":", 1)
            key = key.strip()
            value = value.strip()

            #match and store relevant key-value pairs
            for match_key in keywords:
                if match_key.lower() in key.lower():
                    cleaned_data[match_key] = value
                    break
        else:
            for match_key in keywords:
                if match_key.lower() in item.lower():
                    cleaned_data[match_key] = True

    #if keywords are missing will automatically set it to False
    for key in ["Hardwood Floor", "Skylight", "Balcony", "Central Air", "Open Floorplan", "Basement", "Attic"]:
        if key not in cleaned_data:
            cleaned_data[key] = False

    #handle the school rating values
    for rating in school_ratings:
        level = rating.get("school_level", "").strip()
        score = rating.get("rating", "").strip()
        if "K-5" in level:
            cleaned_data["rating_K_5"] = score
        elif "6-8" in level:
            cleaned_data["rating_6_8"] = score
        elif "9-12" in level:
            cleaned_data["rating_9_12"] = score

    #if school rating values are missing, default to None
    for key in ["rating_K_5", "rating_6_8", "rating_9_12"]:
        if key not in cleaned_data:
            cleaned_data[key] = None

    return cleaned_data
