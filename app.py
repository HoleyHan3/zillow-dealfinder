import streamlit as st
from bs4 import BeautifulSoup
import pandas as pd
import requests
import lxml
import re
from lxml.html.soupparser import fromstring
# Configure logging
import logging

# Define constants
SALE_OR_RENT_OPTIONS = ["For Sale", "For Rent"]
HOME_TYPE_OPTIONS = ["Houses", "Apartments", "Townhomes"]

# Set up logging configuration
logging.basicConfig(level=logging.INFO)


# Streamlit App
def main():
    st.title('Zillow Property Search Results')

    # User input for location
    location = st.text_input("Enter Location (e.g., neighborhood-city-state-zipcode)", "new-york")

    # Validate location input
    if not validate_location(location):
        st.warning("Please enter a valid location containing only letters, numbers, spaces, and hyphens.")
        return

    # Select box for choosing between homes for sale and homes for rent
    sale_or_rent = st.selectbox("Select", SALE_OR_RENT_OPTIONS,index=0)

    # Select box for choosing home types
    home_type = st.selectbox("Select Home Type", HOME_TYPE_OPTIONS,index=0)

    # Select box for choosing the number of listings
    num_listings = st.selectbox("Select Number of Listings", [5, 10, 50, 100],index=0)

    # Button to fetch data
    if st.button('Fetch Zillow Data'):
        zillow_df = fetch_zillow_data(location, sale_or_rent.lower(), home_type.lower(), num_listings)
        if zillow_df.empty:
            st.warning("No data available. Please refine your search criteria.")
        else:
            # Format HTML for display
            html = zillow_df.to_html(escape=False, index=False)
            st.write(html, unsafe_allow_html=True)

# Function to validate location input
def validate_location(location):
    # Check if location contains only letters, spaces, and hyphens
    if not re.match("^[a-zA-Z\s\-0-9]+$", location):
        return False
    return True

# Function to format the search parameter based on user input
def format_search_parameter(user_input):
    # Replace spaces with hyphens
    formatted_parameter = user_input.strip().lower().replace(" ", "-")
    return formatted_parameter
 

# Function to fetch data from Zillow
@st.cache(show_spinner=False)
def fetch_zillow_data(location, sale_or_rent='', home_type='', max_properties=None):
    try:
        # Define the base URL
        base_url = f'https://www.zillow.com/{location}/{home_type}/{sale_or_rent}/'

        # Define request headers
        request_headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'en-US,en;q=0.8',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'
        }

        # List to store property details
        all_addresses = []
        all_prices = []
        all_beds = []
        all_links = []

        # Iterate through pages
        page_num = 1
        properties_fetched = 0
        while True:
            url = f'{base_url}{page_num}_p/' if page_num > 1 else base_url
            with requests.Session() as session:
                response = session.get(url, headers=request_headers)

            # Check if page exists
            if response.status_code != 200:
                break

            # Parse HTML content
            soup = BeautifulSoup(response.content, 'html.parser')

            # Extract property details
            addresses = [address.get_text(strip=True) for address in soup.find_all(class_='list-card-addr')]
            prices = [price.get_text(strip=True) for price in soup.find_all(class_='list-card-price')]
            beds = [bed.get_text(strip=True) for bed in soup.find_all('ul', class_='list-card-details')]
            links = [link['href'] for link in soup.find_all(class_='list-card-link')]

            # Calculate the number of new properties fetched
            num_new_properties = len(addresses)

            # If the number of properties fetched exceeds the maximum or if max_properties is specified
            if max_properties is not None and properties_fetched + num_new_properties > max_properties:
                num_new_properties = max_properties - properties_fetched
                addresses = addresses[:num_new_properties]
                prices = prices[:num_new_properties]
                beds = beds[:num_new_properties]
                links = links[:num_new_properties]

            # Append details to the lists
            all_addresses.extend(addresses)
            all_prices.extend(prices)
            all_beds.extend(beds)
            all_links.extend(links)

            # Update the total number of properties fetched
            properties_fetched += num_new_properties

            # Check if the maximum number of properties has been reached
            if max_properties is not None and properties_fetched >= max_properties:
                break

            page_num += 1

        # Create DataFrame
        df = pd.DataFrame({'Address': all_addresses,
                           'Price': all_prices,
                           'Beds': all_beds,
                           'Link': all_links})

        return df

    except Exception as e:
        logging.error(f"An error occurred while fetching data: {str(e)}")
        return pd.DataFrame()

if __name__ == "__main__":
    main()
