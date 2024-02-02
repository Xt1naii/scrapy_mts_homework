import scrapy
from scrapy.selector import Selector


class WikiFilmsSpider(scrapy.Spider):
    name = "wiki_films"
    allowed_domains = ["ru.wikipedia.org", "https://www.imdb.com/"]
    base_urls = ["https://ru.wikipedia.org/"]

    custom_settings = {
        'FEEDS': {
            'wiki_scraping_result.csv': {'format': 'csv'}
        }
    }

    def start_requests(self):
        url =  "https://ru.wikipedia.org/wiki/Категория:Фильмы_по_алфавиту"
        yield scrapy.Request(url, callback=self.parse_pages)
    
    def parse_pages(self, response):
        for href in response.xpath('//div[@id="mw-pages"]//div[@class="mw-content-ltr"]//li//a/@href').getall():
            url = response.urljoin(href)
            yield scrapy.Request(url, callback=self.parse_film)

        next_page = response.xpath('//div[@id="mw-pages"]/a//@href').getall()[1]
        if next_page:
            yield response.follow(next_page, callback=self.parse_pages)
    
    def parse_film(self, response):
        year = response.xpath('//table//tr[th[contains(., "Год")]]/td//a[last()]//text()').get()
        if year is None:
            year = response.xpath('//table//tr[th[contains(., "показ")]]/td//*[last()]//text()').get()

        film = {
            'title': response.xpath('//table//tr/th[@class="infobox-above"]/text()').get(),
            'genre': response.xpath('//table//tr[th[contains(., "Жанр")]]/td/span//text()').get(),
            'director': response.xpath('//table//tr[th[contains(., "Режиссёр")]]/td//span//text()').get(),
            'country': response.xpath('//table//tr[th[contains(., "Стран")]]/td//span/a//text()').getall(),
            'year': year
        }

        yield film