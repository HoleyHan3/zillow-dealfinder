import scrapy
import json
import re
from urllib.parse import quote


class ZillowSpider(scrapy.Spider):
    name = 'zillowspider'
    allowed_domains = ['zillow.com']
    start_urls = []
    base_url_template = 'https://zillow.com/{}/{}'

    def __init__(self, property_type='sold', max_pages=10, city_names=None, *args, **kwargs):
        super(ZillowSpider, self).__init__(*args, **kwargs)
        self.max_pages = int(max_pages)
        self.property_type = property_type
        self.url_template = self.get_url_template()

        if city_names is not None:
            self.start_urls = [self.url_template.format(self.parse_city_name(name)) for name in city_names.split('|')]

        self.log(', '.join(self.start_urls))

    def get_url_template(self):
        """
        Returns a URL template based on the property type.

        :return: str - The URL template based on the property type.
        """
        url_suffix = 'for-rent/' if self.property_type == 'rental' else 'homes/' if self.property_type == 'unsold' else 'sold/'
        return self.base_url_template.format('{}', url_suffix)


    def parse(self, response):
        """
        Parse the response and extract encoded query search terms. If found, create a results URL and yield a request to parse the page state. Log any errors encountered during parsing.
        Parameters:
            - response: the response object to parse
        Return:
            - None
        """
        try:
            encodedQuerySearchTerms = response.css('script[data-zrr-shared-data-key="mobileSearchPageStore"]::text').re_first(r'^<!--(.*)-->$')
            if encodedQuerySearchTerms:
                queryState = json.loads(encodedQuerySearchTerms).get('queryState', {})
                results_url = self.zillow_search_url_template.format(quote(json.dumps(queryState)))
                yield response.follow(results_url, callback=self.parse_page_state, cb_kwargs={'query_state': queryState})
        except Exception as e:
            self.log(f"Error during parsing: {str(e)}")


def parse_page_state(self, response, page=1, query_state=None):
    """
    Parse the page state from the response.

    Args:
        response: The response object from which to parse the page state.
        page: The page number being parsed (default is 1).
        query_state: The state of the query (default is None).

    Yields:
        dict: A dictionary containing the parsed information for each listing on the page.

    Returns:
        A scrapy request for the next page, if applicable.
    """
    self.log('Parsing page ' + str(page))

    data = response.json()
    next_page = data['cat1']['searchList']['totalPages']

    for listing in data['cat1']['searchResults']['listResults']:
        home_info = listing['hdpData']['homeInfo']
            
        # Extract monthly Zestimate for unsold homes
        monthly_zestimate = (listing.get('zestimate', {}).get('valuationRange', {}).get('low', '') if self.property_type == 'unsold' else None)

        yield {
            'zpid': home_info['zpid'],
            'streetAddress': home_info['streetAddress'],
            'zipcode': home_info['zipcode'],
            'city': home_info['city'],
            'state': home_info['state'],
            'latitude': home_info['latitude'],
            'longitude': home_info['longitude'],
            'price': home_info['price'],
            'dateSold': home_info['dateSold'],
            'bathrooms': home_info['bathrooms'],
            'bedrooms': home_info['bedrooms'],
            'livingArea': home_info['livingArea'],
            'homeType': home_info['homeType'],
            'currency': home_info['currency'],
            'country': home_info['country'],
            'taxAssessedValue': home_info['taxAssessedValue'],
            'lotAreaValue': home_info['lotAreaValue'],
            'lotAreaUnit': home_info['lotAreaUnit'],
            'monthlyZestimate': monthly_zestimate
        }

    if next_page <= self.max_pages:
        next_query_state = query_state.copy() if query_state else {}
        next_query_state.update({"pagination": {"currentPage": page + 1}})
        next_page_url = self.zillow_search_url_template.format(quote(json.dumps(next_query_state)))

        yield scrapy.Request(next_page_url, callback=self.parse_page_state, cb_kwargs={'page': page + 1, 'query_state': next_query_state})

@staticmethod
def parse_city_name(city_name):
    """Parse and format the city name.

    Args:
        city_name (str): The name of the city to be parsed and formatted.

    Returns:
        str: The parsed and formatted city name.
    """
    # Remove leading and trailing whitespaces, convert to lowercase, and replace commas with spaces
    formatted_city_name = '-'.join(city_name.strip().lower().replace(',', '').split())

    return formatted_city_name
