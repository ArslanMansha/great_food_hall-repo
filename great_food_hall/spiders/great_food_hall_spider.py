"""Scraping online shopable items of great food hall"""
import math
import scrapy
from great_food_hall_code.items import GreatFoodHallCodeItem


class GreatFoodHallSpider(scrapy.Spider):
    """Spider."""
    name = "great_food_hall"
    start_urls = ["http://www.greatfoodhall.com/eshop/LoginPage.do"]

    def parse(self, response):
        """Parses links from homepage."""
        sections = response.xpath("//div[@class='item']/a/@href").extract()
        for section in sections:
            yield response.follow(self.start_urls[0], callback=self.refer_homepage,
                                  dont_filter=True,
                                  meta={"cookiejar": response.headers['Set-Cookie'],
                                        "url": section})

    def refer_homepage(self, response):
        """Refers Homepage for distinct cookies."""
        yield response.follow(response.meta['url'], callback=self.set_section_cookie,
                              dont_filter=True,
                              meta={"cookiejar": response.headers['Set-Cookie']})

    def set_section_cookie(self, response):
        """Passes the distinct cookies."""
        yield response.follow(response.url, callback=self.parse_section_pagination,
                              meta={"cookiejar": response.meta['cookiejar']})

    def parse_section_pagination(self, response):
        """Parses the pagination of sections"""
        total_items = response.xpath("//b[@class='totalItem']/text()").extract_first()
        if total_items:
            total_items = int(total_items)
            if total_items > 9:
                last_page = math.ceil(total_items / 9)
                for iterator in range(last_page):
                    next_page = "{}?curPage_1={}".format(response.url.split('?')[0], iterator + 1)
                    yield response.follow(next_page, callback=self.parse_category, dont_filter=True,
                                          meta={"cookiejar": response.meta['cookiejar']})
        else:
            yield response.follow(response.url, callback=self.parse_category,
                                  meta={"cookiejar": response.meta['cookiejar']})

    def parse_category(self, response):
        """Parses the section pages"""
        products = response.xpath("//div[@class='productTmb']/a/@href").extract()
        for product in products:
            yield response.follow(product, callback=self.parse_product, dont_filter=True,
                                  meta={"cookiejar": response.meta['cookiejar']})

    @staticmethod
    def parse_product(response):
        """Parse the Product details."""
        item = GreatFoodHallCodeItem()
        item['cookie'] = list(response.meta['cookiejar'])
        item['item_url'] = response.url
        item['name'] = response.xpath("//title/text()").extract_first()
        item['description'] = response.xpath("//p[@class='description pB5 pL6 typeface-js']"
                                             "/text()").extract()
        item['nutrition'] = response.xpath("//div[@id='nutrition']/table/tr/td/text()").\
            extract_first()

        quantity = response.xpath("//span[@class='ml pB5 pL6']/text()").extract()
        if not quantity:
            quantity = response.xpath("//span[@class='suggest fL pB5 pL6 pR5']/text()")[-1]\
                .extract()
        item['quantity'] = quantity

        price = response.xpath("//*[@class='itemOrgPrice2']/text()").extract_first()
        if not price:
            pricing = {"Old Price": response.xpath("//div[@class='oldPrice pB5']/text()")
                                    .extract_first(),
                       "New Price": response.xpath("//div[@class='newPrice pB5']/text()")
                                    .extract_first()}
        else:
            pricing = {"Old Price": price, "New Price": price}
        item['pricing'] = pricing

        herierachy = response.xpath("//div[@class='breadCrumbArea clearFix']/ul/text()").extract()
        item['herierachy'] = [value for value in herierachy if len(value) > 10][0].strip()

        if response.xpath("//div[@class='btnAddToCart fL']/img"):
            availability = "Out of Stock"
        else:
            availability = "Available"
        item['availability'] = availability

        yield item
