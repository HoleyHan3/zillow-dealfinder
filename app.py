import requests
import re
import json
import pandas as pd
import streamlit as st
import urllib.parse
from bs4 import BeautifulSoup
import xmltodict

# Constants
BASE_URL = 'https://zillow.com/webservice'

# Load default config.json
with open('config.json') as f:
    default_config = json.load(f)

# Streamlit App
st.title('Zillow Property Search')

# User Input Section
st.sidebar.header('Search Parameters')

neighborhood = st.sidebar.text_input('Neighborhood', default_config['neighborhood'])
price_min = st.sidebar.number_input('Minimum Price', value=default_config['filters']['price_min'])
price_max = st.sidebar.number_input('Maximum Price', value=default_config['filters']['price_max'])
# Add more input fields for other parameters like beds, baths, etc.

# Button to Trigger Search
if st.sidebar.button('Search'):
    # Perform Zillow API call based on user input
    try:
        search_results = perform_zillow_search(neighborhood, price_min, price_max)
        display_results(search_results)
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")


def perform_zillow_search(neighborhood, price_min, price_max):
    # Customize parameters based on user input
    ZWSID = default_config['ZWSID']
    city, state = neighborhood.split(', ')
    filters = default_config['filters']

    params = {
        'zws-id': ZWSID,
        'city': city,
        'state': state
    }

    r = requests.get(f'{BASE_URL}/GetRegionChildren.htm', params=params)
    resp = xmltodict.parse(r.text, process_namespaces=True)['http://www.zillow.com/static/xsd/RegionChildren.xsd:regionchildren']
    if r.status_code != 200:
        raise ValueError(resp['message'])
    data = resp['response']

    params = {
        "pagination": {},
        "mapBounds": {
            "west": float(data['region']['longitude']) - 0.5,
            "east": float(data['region']['longitude']) + 0.5,
            "south": float(data['region']['latitude']) - 0.5,
            "north": float(data['region']['latitude']) + 0.5
        },
        "usersSearchTerm": city + ' ' + state,
        "regionSelection": [
            {
                "regionId": int(data['region']['id']),
                "regionType": 6
            }
        ],
        "isMapVisible": True,
        "mapZoom": 12,
        "filterState": {
            "sortSelection": {
                "value": filters.get('sort', 'days')
            },
            "isForRent": {
                "value": filters.get('rent_max', 0) != -1
            },
            "enableSchools": {
                "value": False
            }
        },
        "isListVisible": True
    }

    # Filters
    if filters.get('price_max') != 0:
        params['filterState']['price'] = {'min': price_min, 'max': price_max}

    # Make API call to Zillow
    url = f"https://zillow.com/{city.replace(' ', '-').lower()}-{state.lower()}/?searchQueryState={urllib.parse.quote(str(params))}"
    r = requests.get(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36"})
    soup = BeautifulSoup(r.text, 'lxml')
    listings = soup.find('ul', class_='photo-cards').find_all('li', recursive=False)
    
    results = []
    for i in listings:
        try:
            address = i.article.a.h3.text
            price = i.find('div', class_='list-card-price').text
            rent = i.find('div', class_='list-card-type').text

            is_renting = 'rent' in rent.lower()
            results.append({'address': address, 'price': price, 'rent': rent, 'is_renting': is_renting})
        except Exception as e:
            print(f"Error processing listing: {str(e)}")
    
    return results


def display_results(results):
    st.write('-' * 100)
    for listing in results:
        address = listing['address']
        price = listing['price']
        rent = listing['rent']

        st.write(f'{rent} at {price} - {address}')
        
        if listing['is_renting']:
            st.write("This property is available for rent.")

        # Add more details and formatting as needed
        st.write('-' * 100)
