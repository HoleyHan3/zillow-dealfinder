import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

# Define rate limit (10 requests per minute)
RATE_LIMIT_PER_MINUTE = 10
# Define rate limit periods
RATE_LIMIT_PERIOD_MINUTE = 60  # 60 seconds in a minute

# Function to scrape Zillow listings for a given city and page
def scrape_zillow_listings(city, page):
    """
    Scrapes Zillow listings for a given city and page.

    Args:
        city (str): The city for which listings are scraped.
        page (int): The page number of listings to scrape.

    Returns:
        list: List of dictionaries containing listing information.
    """
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
    """
    Extracts listings from HTML content.

    Args:
        soup (BeautifulSoup): The BeautifulSoup object containing the HTML content.

    Returns:
        list: List of dictionaries containing listing information.
    """
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
    """
    Performs a Zillow property search based on user input.

    Args:
        city (str): The city for which the search is performed.
        num_results (int): The number of results to return.

    Returns:
        list: List of dictionaries containing search results.
    """
    # Attempt to scrape data from Zillow website
    listings = []
    page = 1

    # Initialize variables for rate limit tracking
    requests_count = 0
    start_time = time.time()

    while len(listings) < num_results:
        # Check rate limit
        elapsed_time = time.time() - start_time
        if elapsed_time < RATE_LIMIT_PERIOD_MINUTE and requests_count >= RATE_LIMIT_PER_MINUTE:
            time.sleep(RATE_LIMIT_PERIOD_MINUTE - elapsed_time)
            start_time = time.time()
            requests_count = 0

        new_listings = scrape_zillow_listings(city, page)
        if not new_listings:
            break
        listings.extend(new_listings)
        page += 1
        requests_count += 1

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
            search_results = search_zillow(city, num_results)
            if search_results:
                # Display search results here
                st.write("Search Results:")
                df = pd.DataFrame(search_results)
                st.write("Shape:", df.shape[0])
                st.dataframe(df)
            else:
                st.error("Failed to retrieve search results. Please check the city name and try again.")
        else:
            st.warning("Please enter a city name to search for properties.")

if __name__ == "__main__":
    main()
