import scrapy
import json
import re
from urllib.parse import quote
from itemadapter import ItemAdapter



class ZillowSpider(scrapy.Spider):
    name = 'zillowspider'
    allowed_domains = ['zillow.com']
    start_urls = []
    base_url_template = 'https://zillow.com/{}/{}'
    zillow_search_url_template = 'https://zillow.com/search/GetSearchPageState.htm?searchQueryState={0}&wants=' + quote('{"cat1":["listResults"]}')


    def __init__(self, property_type='sold', max_pages=10, city_names=None, *args, **kwargs):
        super(ZillowSpider, self).__init__(*args, **kwargs)
        self.max_pages = int(max_pages)
        self.property_type = property_type
        self.url_template = self.get_url_template()

        if city_names is not None:
            self.start_urls = [self.url_template.format(self.parse_city_name(name)) for name in city_names.split('|')]

        self.log(', '.join(self.start_urls))

    def get_url_template(self, page=1):
        """
        Returns a URL template based on the property type.

        :return: str - The URL template based on the property type.
        """
        #url_suffix = 'for-rent/' if self.property_type == 'rental' else 'homes/' if self.property_type == 'unsold' else 'sold/'
        #return self.base_url_template.format('{}', url_suffix)
        return f"{self.zillow_search_url_template}/{self.property_type}/page-{page}_p/"


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
        self.log('Parsing page ' + str(page))

        data = response.json()
        next_page = data.get('cat1', {}).get('searchList', {}).get('totalPages')

        #next_page = data['cat1']['searchList']['totalPages']

        for listing in data['cat1']['searchResults']['listResults']:
            adapter = ItemAdapter(
                {
                    'zpid': listing['hdpData']['homeInfo']['zpid'],
                    'streetAddress': listing['hdpData']['homeInfo']['streetAddress'],
                    'zipcode': listing['hdpData']['homeInfo']['zipcode'],
                    'city': listing['hdpData']['homeInfo']['city'],
                    'state': listing['hdpData']['homeInfo']['state'],
                    'latitude': listing['hdpData']['homeInfo']['latitude'],
                    'longitude': listing['hdpData']['homeInfo']['longitude'],
                    'price': listing['hdpData']['homeInfo']['price'],
                    'dateSold': listing['hdpData']['homeInfo']['dateSold'],
                    'bathrooms': listing['hdpData']['homeInfo']['bathrooms'],
                    'bedrooms': listing['hdpData']['homeInfo']['bedrooms'],
                    'livingArea': listing['hdpData']['homeInfo']['livingArea'],
                    'homeType': listing['hdpData']['homeInfo']['homeType'],
                    'taxAssessedValue': listing['hdpData']['homeInfo']['taxAssessedValue'],
                    'lotAreaValue': listing['hdpData']['homeInfo']['lotAreaValue'],
                    'lotAreaUnit': listing['hdpData']['homeInfo']['lotAreaUnit'],
                }
            )

            # Extract monthly Zestimate for unsold homes
            if self.property_type == 'unsold':
                adapter['monthlyZestimate'] = listing.get('zestimate', {}).get('valuationRange', {}).get('low', '')

            yield adapter.asdict()

        if next_page <= self.max_pages:
            next_query_state = query_state.copy() if query_state else {}
            next_query_state.update({"pagination": {"currentPage": page + 1}})
            next_page_url = self.get_url_template(page=page + 1)

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
