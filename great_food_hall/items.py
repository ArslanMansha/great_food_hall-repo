# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class GreatFoodHallCodeItem(scrapy.Item):
    name = scrapy.Field()
    description = scrapy.Field()
    pricing = scrapy.Field()
    herierachy = scrapy.Field()
    weblink = scrapy.Field()
    item_url = scrapy.Field()
    quantity = scrapy.Field()
    herierachy = scrapy.Field()
    availability = scrapy.Field()
    nutrition = scrapy.Field()
    cookie = scrapy.Field()
