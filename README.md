# Nationwide-House-Price-Prediction

This project aims to scrape housing listings from Redfin across the United States, build a comprehensive real estate dataset (~1M+ listings), and develop a machine learning model to predict home prices based on property and location features. A final interactive dashboard will visualize trends and predictions.

## Project Workflow

### 1. Web Crawling and Web Scraping
- Automate the crawling of Redfin city or zip code pages across the U.S.
- Scrape key listing data: price, address, zip code, bedrooms, bathrooms, square footage, lot size, year built, etc.
- Navigate through pagination and extract structured data.
- Store scraped data locally in CSV and/or push to an SQL database.

### 2. Build and Structure the Database
- Clean and normalize the raw data.
- Store into SQLite/PostgreSQL for efficient querying and data integrity.
- (Optional) Enrich with external datasets: census income data, school quality ratings, etc.

### 3. Exploratory Data Analysis (EDA)
- Visualize trends by zip code, region, home size, and more.
- Identify missing values, outliers, and correlations.
- Use plots to explore distribution of prices, square footage, and room counts.

### 4. Predictive Modeling
- Feature engineering: one-hot encoding, interaction terms, geographic clustering, etc.
- Train and evaluate multiple models (Linear Regression, Random Forest, XGBoost, etc.).
- Measure performance using RMSE, MAE, and R².
- Apply SHAP values to interpret feature importance.

### 5. Dashboard Development
- Create an interactive dashboard to:
  - Explore housing trends by region
  - Input property features and predict home price
 
## Key Features to Capture
- Zip code, address
- Bedrooms, bathrooms
- Square footage, lot size
- Year built, renovation year
- HOA fees, garage spaces, pool/fireplace
- Location data: city, state, latitude/longitude
- Enrichment: median income, school ratings, crime index
