# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# pipelines.py
import json
from itemadapter import ItemAdapter
from scrapy.exporters import JsonItemExporter, CsvItemExporter
from scrapy.exceptions import DropItem

class CustomExportPipeline:
    def __init__(self):
        self.json_exporter = None
        self.xlsx_exporter = None

    def open_spider(self, spider):
        self.json_exporter = JsonItemExporter(open('output.json', 'wb'), indent=2)
        self.csv_exporter = CsvItemExporter(open('output.csv', 'wb'))

        self.json_exporter.start_exporting()
        self.csv_exporter.start_exporting()

    def close_spider(self, spider):
        self.json_exporter.finish_exporting()
        self.csv_exporter.finish_exporting()

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        # Export to JSON
        self.json_exporter.export_item(adapter)

        # Export to XLSX
        self.csv_exporter.export_item(adapter)

        return item


class DuplicatesPipeline:
    def __init__(self):
        """
        Initializes the object and initializes the ids_seen attribute as an empty set.
        """
        self.ids_seen = set()

    def process_item(self, item, spider):
        """
        Process the given item and spider, checking for duplicates and returning the item.
        
        :param item: the item to be processed
        :param spider: the spider associated with the item
        :return: the processed item
        """
        adapter = ItemAdapter(item)
        if 'zpid' in adapter and adapter['zpid'] in self.ids_seen:
            raise DropItem(f"Duplicate item found: {item!r}")
        else:
            self.ids_seen.add(adapter['zpid'])
            return item
