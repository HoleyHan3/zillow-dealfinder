import streamlit as st
import requests
from bs4 import BeautifulSoup
import json
import xmltodict

# Access the secret API key
@st.cache
def get_zillow_api_key():
    try:
        return st.secrets["zillow_api_key"]
    except Exception as e:
        st.warning("Failed to retrieve Zillow API key. Please check your secrets.")
        return None

# Define headers for HTTP requests
req_headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'en-US,en;q=0.8',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'
}

# Function to scrape Zillow listings for a given city and page
def scrape_zillow_listings(city, page):
    # Perform web scraping of Zillow listings
    listings = []

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
def search_zillow(city, num_results):
    # Attempt to scrape data from Zillow website
    listings = []
    page = 1
    while len(listings) < num_results:
        new_listings = scrape_zillow_listings(city, page)
        if not new_listings:
            break
        listings.extend(new_listings)
        page += 1
    return listings[:num_results]

# Streamlit App
def main():
    st.title('Zillow Property Search')

    # User Input Section
    st.sidebar.header('Search Parameters')
    city = st.sidebar.text_input('City', 'New York City')
    num_results = st.sidebar.number_input('Number of Results', min_value=1, value=10)

    # Button to Trigger Search
    if st.sidebar.button('Search'):
        if city:
            # Perform Zillow property search based on user input
            zillow_api_key = get_zillow_api_key()
            if zillow_api_key:
                search_results = search_zillow(city, num_results)
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

if __name__ == "__main__":
    main()
