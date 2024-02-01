import requests
import re
import json
import pandas as pd
import streamlit as st
import time
import random

# Define the base search URL based on the user's input
search_query = st.text_input("Enter Zillow Search Query", "new-york-ny/")  # Example: new-york-ny/ or 11233/
base_url = f'https://www.zillow.com/{search_query}'

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

    # Fetch data from the current page
    with requests.Session() as s:
        try:
            r = s.get(search_url, headers=req_headers)
            if r.status_code == 200:
                data = json.loads(re.search(r'!--(\{"queryState".*?)-->', r.text).group(1))
                listings = data['cat1']['searchResults']['listResults']
                df = df.append(listings, ignore_index=True)
                page += 1
                time.sleep(random.uniform(1, 3))  # Add a random delay between requests
            else:
                st.error(f"Failed to retrieve Zillow listings for page {page}")
                break
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
            break

# Drop unnecessary columns
df = df.drop('hdpData', axis=1)

# Remove duplicate entries based on 'zpid'
df = df.drop_duplicates(subset='zpid', keep="last")

# Fill NaN values in 'zestimate' column with 0
df['zestimate'] = df['zestimate'].fillna(0)

# Calculate 'best_deal' column
df['best_deal'] = df['unformattedPrice'] - df['zestimate']

# Sort DataFrame based on 'best_deal' column
df = df.sort_values(by='best_deal', ascending=True)

# Streamlit App
def main():
    st.title('Zillow Property Search Results')

    # Display the shape of the DataFrame
    st.write('Shape:', df.shape)

    # Display the top 20 rows with selected columns
    st.write(df[['id', 'address', 'beds', 'baths', 'area', 'price', 'zestimate', 'best_deal']].head(20))

if __name__ == "__main__":
    main()
