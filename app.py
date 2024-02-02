import streamlit as st
from bs4 import BeautifulSoup
import pandas as pd
import requests
import regex as re
import lxml
from lxml.html.soupparser import fromstring
# Configure logging
import logging

# Set up logging configuration
logging.basicConfig(level=logging.INFO)

# Function to fetch data from Zillow
@st.cache(show_spinner=False)
def fetch_zillow_data(city, sale_or_rent, home_type):
    if sale_or_rent == 'for_sale':
        url = f'https://www.zillow.com/homes/for_sale/{city}/{home_type}/'
    elif sale_or_rent == 'for_rent':
        url = f'https://www.zillow.com/homes/for_rent/{city}/{home_type}/'

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

    # User input for city
    city = st.text_input("Enter City", "seattle")

    # Select box for choosing between homes for sale and homes for rent
    sale_or_rent = st.selectbox("Select", ["For Sale", "For Rent"])

    # Select box for choosing home types
    home_type = st.selectbox("Select Home Type", ["houses", "apartments", "townhomes"])

    # Map the selection to the corresponding URL parameter
    if sale_or_rent == "For Sale":
        sale_or_rent_param = "for_sale"
    else:
        sale_or_rent_param = "for_rent"

    # Button to fetch data
    if st.button('Fetch Zillow Data'):
        zillow_df = fetch_zillow_data(city, sale_or_rent_param, home_type)

        if zillow_df.empty:
            st.warning("No data available. Please check your search query and try again.")
        else:
            # Format HTML for display
            html = zillow_df.to_html(escape=False, index=False)
            st.write(html, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
