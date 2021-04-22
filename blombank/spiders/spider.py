import scrapy
from scrapy import FormRequest

from scrapy.loader import ItemLoader

from ..items import BlombankItem
from itemloaders.processors import TakeFirst


class BlombankSpider(scrapy.Spider):
	name = 'blombank'
	start_urls = ['https://www.blombank.com/Corporate/ListingNews.aspx?lang=1&pageid=63']

	def parse(self, response):
		post_links = response.xpath('//div[@class="readMore"]/a/@href').getall()
		yield from response.follow_all(post_links, self.parse_post)

		next_page = response.xpath('//a[@class="nextArrow"]/@href').getall()
		if next_page:
			yield FormRequest.from_response(response, formdata={'__EVENTTARGET': 'ctl00$PlaceHolderBodyNormal$lbtnNext'}, callback=self.parse)

	def parse_post(self, response):
		title = response.xpath('//h3/text()').get()
		description = response.xpath('//div[@class="contentCont"]//p//text()[normalize-space() and not(ancestor::a)]').getall()
		description = [p.strip() for p in description if '{' not in p]
		description = ' '.join(description).strip()
		date = response.xpath('//div[@class="listingDate"]/text()').get()

		item = ItemLoader(item=BlombankItem(), response=response)
		item.default_output_processor = TakeFirst()
		item.add_value('title', title)
		item.add_value('description', description)
		item.add_value('date', date)

		return item.load_item()
