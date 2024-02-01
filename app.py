import requests
import re
import json
import pandas as pd
import streamlit as st
import time
import random
import logging
from retrying import retry  # Install using pip install retrying

# Configure logging
logging.basicConfig(level=logging.INFO)

# Define a retry decorator for network requests
@retry(stop_max_attempt_number=3, wait_random_min=1000, wait_random_max=3000)
def fetch_data_with_retry(url, headers):
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response

# Function to fetch data from Zillow
def fetch_zillow_data(base_url):
    # Define headers for HTTP requests
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.59',
        # Add more user agents as needed
    ]

    # Initialize an empty DataFrame
    df = pd.DataFrame()

    # Fetch data from multiple pages of search results
    page = 1
    while True:
        # Construct the search URL for the current page
        search_url = f'{base_url}/{page}_p/'

        # Rotate user-agent header
        user_agent = random.choice(user_agents)
        req_headers = {
            'User-Agent': user_agent,
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'en-US,en;q=0.8',
            'upgrade-insecure-requests': '1'
        }

        # Fetch data from the current page with retry logic
        try:
            response = fetch_data_with_retry(search_url, headers=req_headers)
            if response.status_code == 200:
                data = json.loads(re.search(r'!--(\{"queryState".*?)-->', response.text).group(1))
                listings = data['cat1']['searchResults']['listResults']
                df = df.append(listings, ignore_index=True)
                page += 1
                time.sleep(random.uniform(1, 3))  # Add a random delay between requests
            else:
                logging.error(f"Failed to retrieve Zillow listings for page {page}. Status code: {response.status_code}")
                break
        except Exception as e:
            logging.error(f"An error occurred while fetching data: {str(e)}")
            break

    # Drop unnecessary columns
    if not df.empty:
        df = df.drop('hdpData', axis=1)

        # Remove duplicate entries based on 'zpid'
        df = df.drop_duplicates(subset='zpid', keep="last")

        # Fill NaN values in 'zestimate' column with 0
        if 'zestimate' in df.columns:
            df['zestimate'] = df['zestimate'].fillna(0)

        # Calculate 'best_deal' column if 'unformattedPrice' and 'zestimate' columns exist
        if 'unformattedPrice' in df.columns and 'zestimate' in df.columns:
            df['best_deal'] = df['unformattedPrice'] - df['zestimate']

        # Sort DataFrame based on 'best_deal' column if it exists
        if 'best_deal' in df.columns:
            df = df.sort_values(by='best_deal', ascending=True)

    return df

# Streamlit App
def main():
    st.title('Zillow Property Search Results')

    # Define the base search URL based on the user's input
    search_query = st.text_input("Enter Zillow Search Query", "new-york-ny/")  # Example: new-york-ny/ or 11233/
    base_url = f'https://www.zillow.com/{search_query}'

    # Add a select box for search type
    search_type = st.selectbox('Select Search Type', ['For Sale', 'For Rent'])

    if search_type == 'For Sale':
        # Set the base URL for homes for sale
        base_url = 'https://www.zillow.com/new-york-ny/'
    else:
        # Set the base URL for homes for rent
        base_url = 'https://www.zillow.com/new-york-ny/rentals/'

    # Button to trigger Zillow data fetching
    if st.button('Fetch Zillow Data'):
        # Fetch Zillow data
        zillow_df = fetch_zillow_data(base_url)

        if zillow_df.empty:
            st.warning("No data available. Please check your search query and try again.")
        else:
            # Display the shape of the DataFrame
            st.write('Shape:', zillow_df.shape)

            # Display the top 20 rows with selected columns
            st.write(zillow_df[['id', 'address', 'beds', 'baths', 'area', 'price', 'zestimate', 'best_deal']].head(20))

if __name__ == "__main__":
    main()
