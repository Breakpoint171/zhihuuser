# -*- coding: utf-8 -*-
import json
import scrapy
from zhihuuser.items import ZhihuuserItem


class ZhihuSpider(scrapy.Spider):
    name = 'zhihu'
    allowed_domains = ['www.zhihu.com']
    start_urls = ['http://www.zhihu.com/']
    start_url = 'https://www.zhihu.com/api/v4/members/{user}/followers?include={include}&offset={offset}&limit={limit}'
    followers_query = 'data[*].answer_count,articles_count,gender,follower_count,' \
                      'is_followed,is_following,badge[?(type=best_answerer)].topics'
    start_user = 'zhang-xi-ting'

    def start_requests(self):
        yield scrapy.Request(
            self.start_url.format(user=self.start_user, include=self.followers_query, offset=0, limit=20),
            callback=self.parse)

    def parse(self, response):
        result = json.loads(response.text)
        item = ZhihuuserItem()
        if 'data' in result.keys():
            for i in result.get('data'):
                for field in item.fields:
                    item[field] = i.get(field)

                yield scrapy.Request(
                    self.start_url.format(user=i.get('url_token'), include=self.followers_query, offset=0, limit=20),
                    callback=self.parse)
                yield item
        if 'paging' in result.keys() and result.get('paging').get('is_end') is False:
            next_page = result.get('paging').get('next')
            yield scrapy.Request(url=next_page, callback=self.parse)
