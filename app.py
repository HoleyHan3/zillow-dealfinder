import streamlit as st
import requests
from bs4 import BeautifulSoup
import json
import xmltodict
from streamlit.secrets import Secrets

# Load secrets
secrets = Secrets()
zillow_api_key = secrets["zillow_api_key"]

# Define headers for HTTP requests
req_headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'en-US,en;q=0.8',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'
}

# Function to scrape home details from Zillow URL
def scrape_home_details(url):
    with requests.Session() as s:
        r = s.get(url, headers=req_headers)
    soup = BeautifulSoup(r.content, 'html.parser')
    price = soup.find('span', {'class': 'zsg-photo-card-price'}).text.strip()
    info = soup.find('span', {'class': 'zsg-photo-card-info'}).text.strip()
    address = soup.find('span', {'itemprop': 'address'}).text.strip()
    monthly_payment = soup.find('div', {'data-testid': 'non-personalized-monthly-payment'}).text.strip()
    return price, info, address, monthly_payment

# Function to scrape Zillow listings for a given city
def scrape_zillow_listings(city):
    # Perform web scraping of Zillow listings
    listings = []

    # Sample URLs for demonstration, you need to implement pagination logic
    for page in range(1, 3):  # Scrapes first 2 pages
        url = f'https://www.zillow.com/homes/for_sale/{city}/{page}_p/'
        # Make HTTP request and scrape listings from the page
        with requests.Session() as session:
            response = session.get(url)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                listings.extend(extract_listings_from_html(soup))
            else:
                st.error(f"Failed to retrieve Zillow listings for page {page}")
    
    return listings

# Function to extract listings from HTML content
def extract_listings_from_html(soup):
    listings = []
    cards = soup.find_all('article', {'class': 'list-card'})
    for card in cards:
        listing = {}
        listing['price'] = card.find('div', {'class': 'list-card-price'}).text.strip()
        listing['address'] = card.find('address').text.strip()
        listing['details_link'] = card.find('a', {'class': 'list-card-link'}).get('href')
        listings.append(listing)
    return listings

# Function to perform Zillow property search based on user input
def search_zillow(city):
    # Attempt to scrape data from Zillow website
    listings = scrape_zillow_listings(city)
    if listings:
        return listings
    else:
        # Fallback to Zillow API if scraping fails
        scrape_zillow_api(city)

# Streamlit App
st.title('Zillow Property Search')

# User Input Section
st.sidebar.header('Search Parameters')
city = st.sidebar.text_input('City', 'New York City')

# Button to Trigger Search
if st.sidebar.button('Search'):
    if city:
        # Perform Zillow property search based on user input
        search_results = search_zillow(city)
        if search_results:
            st.write("Search Results:")
            # Display search results here
            for i, listing in enumerate(search_results, start=1):
                st.write(f"Listing {i}:")
                st.write(f"Price: {listing['price']}")
                st.write(f"Address: {listing['address']}")
                st.write(f"Details Link: {listing['details_link']}")
        else:
            st.error("Failed to retrieve search results. Please check the city name and try again.")
    else:
        st.warning("Please enter a city name to search for properties.")
