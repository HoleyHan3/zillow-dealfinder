import scrapy

class ZillowItem(scrapy.Item):
    url = scrapy.Field()
    name = scrapy.Field()
    floor_size = scrapy.Field()
    street_address = scrapy.Field()
    address_locality = scrapy.Field()
    address_region = scrapy.Field()
    postal_code = scrapy.Field()
    latitude = scrapy.Field()
    longitude = scrapy.Field()
    real_estate_type = scrapy.Field()
    open_house_start_date = scrapy.Field()
    open_house_end_date = scrapy.Field()
    open_house_description = scrapy.Field()
    image_url = scrapy.Field()
    price = scrapy.Field()
    price_currency = scrapy.Field()
    availability = scrapy.Field()
    zestimate_value = scrapy.Field()

    # add more fields as needed

