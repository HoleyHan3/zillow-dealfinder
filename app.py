import streamlit as st
from bs4 import BeautifulSoup
import pandas as pd
import requests
import lxml
from lxml.html.soupparser import fromstring
# Configure logging
import logging

# Set up logging configuration
logging.basicConfig(level=logging.INFO)

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

@st.cache(show_spinner=False)
# Function to fetch data from Zillow
def fetch_zillow_data(location, sale_or_rent='', home_type=''):
    # Define the base URL
    base_url = 'https://www.zillow.com/'

    # Construct the URL based on the provided parameters
    url = f'{base_url}{location}/{home_type}/{sale_or_rent}/'

    # Define request headers
    request_headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-US,en;q=0.8',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'
    }

    # Send HTTP request
    with requests.Session() as session:
        response = session.get(url, headers=request_headers)

    # Parse HTML content
    soup = BeautifulSoup(response.content, 'html.parser')

    # Extract property details
    addresses = [address.get_text(strip=True) for address in soup.find_all(class_='list-card-addr')]
    prices = [price.get_text(strip=True) for price in soup.find_all(class_='list-card-price')]
    beds = [bed.get_text(strip=True) for bed in soup.find_all('ul', class_='list-card-details')]
    links = [link['href'] for link in soup.find_all(class_='list-card-link')]

    # Create DataFrame
    df = pd.DataFrame({'Address': addresses, 
                       'Price': prices, 
                       'Beds': beds, 
                       'Link': links})

    return df

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
    sale_or_rent = st.selectbox("Select", ["For Sale", "For Rent"])
        # Map the selection to the corresponding URL parameter
        if sale_or_rent == "For Sale":
            sale_or_rent_param = "for_sale"
        else:
            sale_or_rent_param = "for_rent"
    # Select box for choosing home types
    home_type = st.selectbox("Select Home Type", ["Houses", "Apartments", "Townhomes"])

   # Button to fetch data
    if st.button('Fetch Zillow Data'):
        if city.strip() == "":
            st.warning("Please enter a valid city.")
        else:
            zillow_df = fetch_zillow_data(city, sale_or_rent_param, home_type)

            if zillow_df.empty:
                st.warning("No data available. Please refine your search criteria.")
            else:
                # Format HTML for display
                html = zillow_df.to_html(escape=False, index=False)
                st.write(html, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
