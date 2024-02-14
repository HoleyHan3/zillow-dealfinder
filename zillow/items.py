import scrapy

class ZillowItem(scrapy.Item):
    zpid = scrapy.Field()
    streetAddress = scrapy.Field()
    zipcode = scrapy.Field()
    city = scrapy.Field()
    state = scrapy.Field()
    latitude = scrapy.Field()
    longitude = scrapy.Field()
    price = scrapy.Field()
    dateSold = scrapy.Field()
    bathrooms = scrapy.Field()
    bedrooms = scrapy.Field()
    livingArea = scrapy.Field()
    homeType = scrapy.Field()
    taxAssessedValue = scrapy.Field()
    lotAreaValue = scrapy.Field()
    lotAreaUnit = scrapy.Field()
    monthlyZestimate = scrapy.Field()

    def __init__(self, *args, **kwargs):
        super(ZillowItem, self).__init__(*args, **kwargs)
        # Make dateSold optional
        self.fields['dateSold'].required = False
