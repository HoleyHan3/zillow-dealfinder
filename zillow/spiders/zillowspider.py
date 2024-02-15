import scrapy
import json
from urllib.parse import quote
from itemadapter import ItemAdapter
from zillow.items import ZillowItem

class ZillowSpider(scrapy.Spider):
    name = 'zillowspider'
    allowed_domains = ['zillow.com']
    start_urls = []
    base_url_template = 'https://zillow.com/{}/{}'

    def __init__(self, listing_category='buy', max_pages=10, city_names=None, *args, **kwargs):
        """
        Constructor for initializing the web scraping spider.

        Args:
            listing_category (str): Type of listing to scrape, default is 'all'.
            max_pages (int): Maximum number of pages to scrape, default is 10.
            city_names (str): Pipe-separated list of city names to scrape.

        Returns:
            None
        """
        super().__init__(*args, **kwargs)
        self.max_pages = int(max_pages)
        self.listing_category = listing_category
        self.url_template = self.get_url_template()

        self.city_names = city_names
        if city_names:
            self.start_urls = [self.url_template.format(self.parse_city_name(name)) for name in city_names.split('|')]

        self.log(', '.join(self.start_urls) if hasattr(self, 'start_urls') else '')
    
    def start_requests(self):
        """
        Custom method to start requests. Overrides the base class method.
        """
        city_names = getattr(self, 'city_names', None)
        if city_names:
            self.start_urls = [self.url_template.format(self.parse_city_name(name)) for name in city_names.split('|')]
        self.log(', '.join(self.start_urls) if hasattr(self, 'start_urls') else '')
        yield from super().start_requests()


    def get_url_template(self, location='new-york-ny', listing_category=None, sorting='', page=1):
        """
        Returns a URL template based on the provided parameters.

        :param location: str - The location for the search (e.g., 'new-york-ny', 'queens-ny','brooklyn-new-york-ny-11233').
                        Defaults to 'new-york-ny' if not provided.
        :param listing_category: str - optional - The type of listing category (e.g., 'buy', 'rentals', 'sold').
        :param sorting: str - optional - The sorting option (e.g., 'newest', 'under_400000').
        :param page: int - The page number.
        :return: str - The constructed URL template.
        """
        base_url = f"https://www.zillow.com/{location}/"

        if listing_category:
            base_url += f"{listing_category}/{page}_p/"

        if sorting:
            return f"{base_url}{sorting}/{page}_p/"
        else:
            return f"{base_url}{page}_p/"


    def parse(self, response):
        # Extract JSON-LD listings from the script tag
        script_data = response.css('script[type="application/ld+json"]::text').getall()

        for script_content in script_data:
            # Load JSON content
            try:
                json_data = json.loads(script_content)
            except json.JSONDecodeError:
                self.log(f"Failed to decode JSON: {script_content}")
                continue

            # Check if the JSON represents a valid real estate type
            real_estate_type = json_data.get('@type', '')
            if real_estate_type:
                item = ZillowItem()

                # Extract relevant information
                item['real_estate_type'] = real_estate_type
                item['property_name'] = json_data.get('name', '')
                item['floor_size'] = json_data.get('floorSize', {}).get('value', '')
                item['street_address'] = json_data.get('address', {}).get('streetAddress', '')
                item['locality'] = json_data.get('address', {}).get('addressLocality', '')
                item['region'] = json_data.get('address', {}).get('addressRegion', '')
                item['postal_code'] = json_data.get('address', {}).get('postalCode', '')
                item['latitude'] = json_data.get('geo', {}).get('latitude', '')
                item['longitude'] = json_data.get('geo', {}).get('longitude', '')
                item['url'] = json_data.get('url', '')

                # Yield the item for further processing in pipelines
                yield item
                yield scrapy.Request(item['url'], callback=self.parse_home_details)

    def parse_home_details(self, response):
        # Extract details from the home details page
        zestimate_script = response.css('div[data-testid="home-details-chip-container"] script::text').get()

        if zestimate_script:
            # Parse the script content
            try:
                zestimate_data = json.loads(zestimate_script)
            except json.JSONDecodeError:
                self.log(f"Failed to decode JSON: {zestimate_script}")
                return

            # Extract the desired information from the script
            zestimate_value = zestimate_data.get('homeValue', {}).get('amount', '')
            if zestimate_value:
                self.log(f"Zestimate Value: {zestimate_value}")
                # You can process or store this information as needed

        """
        Parse the response and extract encoded query search terms. If found, create a results URL and yield a request to parse the page state. Log any errors encountered during parsing.
        Parameters:
            - response: the response object to parse
        Return:
            - None
        """
        """try:
            encodedQuerySearchTerms = response.css('script[data-zrr-shared-data-key="mobileSearchPageStore"]::text').re_first(r'^<!--(.*)-->$')
            if encodedQuerySearchTerms:
                queryState = json.loads(encodedQuerySearchTerms).get('queryState', {})
                results_url = self.base_url_template.format(quote(json.dumps(queryState)))
                yield response.follow(results_url, callback=self.parse_page_state, cb_kwargs={'query_state': queryState})
        except json.JSONDecodeError as e:
            self.log(f"Error during parsing JSON: {str(e)}")
        """

    def parse_page_state(self, response, page=1, query_state=None):
        self.log('Parsing page ' + str(page))

        data = response.json()
        search_results = data.get('cat1', {}).get('searchResults', {}).get('listResults', [])

        for listing in search_results:
            adapter = ItemAdapter({
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
                'listing_category': self.listing_category
            })

            # Extract monthly Zestimate for unsold homes listed as "for_sale"
            if self.listing_category == 'for_sale':
                adapter['monthlyZestimate'] = listing.get('zestimate', {}).get('valuationRange', {}).get('low', '')

             # Print the item to the console
            print(adapter.asdict())


        if next_page := data.get('cat1', {}).get('searchList', {}).get('totalPages') and next_page <= self.max_pages:
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
