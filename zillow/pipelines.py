# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

# pipelines.py
import json
from itemadapter import ItemAdapter
from scrapy.exporters import JsonItemExporter, CsvItemExporter
from scrapy.exceptions import DropItem

class JsonExportPipeline:
    def __init__(self):
        self.json_exporter = None

    def open_spider(self, spider):
        self.json_exporter = JsonItemExporter(open('output.json', 'wb'), indent=2)
        self.json_exporter.start_exporting()

    def close_spider(self, spider):
        self.json_exporter.finish_exporting()

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        # Export to JSON
        self.json_exporter.export_item(adapter)
        return item


class CsvExportPipeline:
    def __init__(self):
        self.csv_exporter = None

    def open_spider(self, spider):
        self.csv_exporter = CsvItemExporter(open('output.csv', 'wb'))
        self.csv_exporter.start_exporting()

    def close_spider(self, spider):
        self.csv_exporter.finish_exporting()

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        # Export to CSV
        self.csv_exporter.export_item(adapter)
        return item


class DuplicatesPipeline:
    def __init__(self):
        self.ids_seen = set()

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        if 'zpid' in adapter and adapter['zpid'] in self.ids_seen:
            raise DropItem(f"Duplicate item found: {item!r}")
        else:
            self.ids_seen.add(adapter['zpid'])
            return item
