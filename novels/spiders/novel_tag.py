# -*- coding: utf-8 -*-
import copy
import time
import re

import scrapy
from scrapy.http import Request
from scrapy_redis.spiders import RedisSpider

from ..items import NovelsTagItem

from ..utils import changeChineseNumToArab

CATEGORY_MAPS = {
    '玄幻奇幻': 1,
    '修真武侠': 2,
    '都市言情': 3,
    '历史军事': 4,
    '同人名著': 5,
    '游戏竞技': 6,
    '科幻灵异': 7,
    '耽美动漫': 8
}


class NovelTagSpider(RedisSpider):
    name = 'novel_tag'
    allowed_domains = ['35kushu.com']
    redis_key = "novel:start_ulrs"
    start_urls = ['https://www.35kushu.com']

    def parse(self, response):
        # tags链接
        tag_url = response.xpath(
            '//div[@class="menu_list_id lan1"]/li/a/@href | //div[@class="menu_list_id lan1"]/li/a/text()').extract()
        tag_urls = [tag_url[i:i + 2] for i in range(0, len(tag_url), 2)]

        # 单例模式
        # tu = tag_urls[0]
        # tag_url = self.start_urls[0] + tu[0]
        # category = tu[1]
        # category_id = CATEGORY_MAPS.get(category)
        # meta = {
        #     "category_id": copy.deepcopy(category_id),
        #     "category": copy.deepcopy(category)
        # }
        # yield Request(tag_url, meta=copy.deepcopy(meta), callback=self.parse_tag_detail)

        for tu in tag_urls[:8]:
            tag_url = self.start_urls[0] + tu[0]
            category = tu[1]

            category_id = CATEGORY_MAPS.get(category)
            meta = {
                "category_id": copy.deepcopy(category_id),
                "category": copy.deepcopy(category)
            }

            # print(meta)
            #
            # {'category_id': 1, 'category': '玄幻奇幻'}
            # {'category_id': 2, 'category': '修真武侠'}
            # {'category_id': 3, 'category': '都市言情'}
            # {'category_id': 4, 'category': '历史军事'}
            # {'category_id': 5, 'category': '同人名著'}
            # {'category_id': 6, 'category': '游戏竞技'}
            # {'category_id': 7, 'category': '科幻灵异'}
            # {'category_id': 8, 'category': '耽美动漫'}

            # 下一步
            yield Request(tag_url, meta=copy.deepcopy(meta), callback=self.parse_tag_detail)

    def parse_tag_detail(self, response):
        # 传入上层meta
        meta_start = response.meta
        novel_info_1 = response.xpath('//div[@id="centerl"]/div[@id="content"]/table/tr[not(@align)]')

        # 单例测试
        # ni1 = novel_info_1[0]
        # tdd = ni1.xpath('td')
        # article_url = self.start_urls[0] + tdd[0].xpath('a/@href').extract_first(default=' ')
        # article_title = tdd[0].xpath('a/text()').extract_first(default=' ')
        # lastest_title = tdd[1].xpath('a/text()').extract_first(default=' ')
        # author = tdd[2].xpath('a/text()').extract_first(default=" ")
        # words = tdd[3].xpath('text()').extract_first(default=" ")
        #
        # status = tdd[5].xpath('a/text()').extract_first(default=" ")
        # if status == "连载中":
        #     is_full = 0
        #     # status = 0
        # elif status == "已完成":
        #     is_full = 1
        #     # status = 1
        # else:
        #     # ?
        #     is_full = 2
        #     # status = 2
        # # 暂时
        # status = 1
        # meta = response.meta
        # meta["article_url"] = article_url
        # meta["title"] = article_title
        # meta["is_full"] = is_full
        # meta["status"] = status
        # meta["author"] = author
        # meta["last_chapter"] = lastest_title
        # meta["article_url_base"] = article_url[33:]
        # lastest_url_base = self.start_urls[0] + tdd[1].xpath('a/@href').extract_first(default=' ')
        # lastest_chapter_id = lastest_url_base.split('/')[-1][:-5]
        # meta["lastest_chapter_id"] = lastest_chapter_id
        # meta['words'] = words
        #
        # print(meta)
        #
        # # print(meta)
        # # {'category_id': 1, 'category': '玄幻奇幻', 'depth': 1, 'download_timeout': 180.0,
        # #  'download_slot': 'www.35kushu.com', 'download_latency': 0.462005615234375,
        # #  'article_url': 'https://www.35kushu.com/35zwhtml/70/70881/', 'title': '万古帝尊', 'is_full': 2, 'status': 1,
        # #  'author': ' ', 'last_chapter': ' 第九百 零八章 解决寄生虫'}
        #
        # yield Request(article_url, meta=meta, callback=self.parse_menu)

        for ni1 in novel_info_1:
            tdd = ni1.xpath('td')
            article_url = self.start_urls[0] + tdd[0].xpath('a/@href').extract_first(default=' ')
            article_title = tdd[0].xpath('a/text()').extract_first(default=' ')
            lastest_url_base = self.start_urls[0] + tdd[1].xpath('a/@href').extract_first(default=' ')
            lastest_chapter_id = lastest_url_base.split('/')[-1][:-5]
            # print(response.meta['category'], article_title, lastest_url_base)
            lastest_title = tdd[1].xpath('a/text()').extract_first(default=' ')
            author = tdd[2].xpath('text()').extract_first(default=" ")
            words = tdd[3].xpath('text()').extract_first(default=" ")
            status = tdd[5].xpath('a/text()').extract_first(default=" ")
            print(status)

            if status == "连载中":
                is_full = 0
                # status = 0
            elif status == "已完成":
                is_full = 1
                # status = 1
            else:
                # ?
                is_full = 2
                # status = 2

            # 暂时
            status = 1
            meta = response.meta
            meta["article_url"] = article_url
            meta["article_title"] = article_title
            meta["is_full"] = is_full
            meta["status"] = status
            meta["author"] = author
            meta["last_chapter"] = lastest_title
            meta["article_url_base"] = article_url[33:]
            meta["lastest_chapter_id"] = lastest_chapter_id
            meta["words"] = words
            # print("words", words)
            yield Request(article_url, meta=meta, callback=self.parse_menu)

        next_page = response.xpath('//div[@class="pagelink"]/a[@class="next"]/@href').extract_first()
        current_page = response.xpath('//div[@class="pagelink"]/strong/text()').extract_first()
        # print(response.meta['category'], "current_page", current_page)
        if next_page and next_page <= "130":
            next_page = self.start_urls[0] + next_page
            yield Request(next_page, meta=meta_start, callback=self.parse_tag_detail)

    def parse_menu(self, response):
        menu_list = response.xpath('//div[@id="indexmain"]//div[@id="list"]/dl/dd/a/@title '
                                   '| //div[@id="indexmain"]//div[@id="list"]/dl/dd/a/@href ').extract()
        head_list = response.xpath(
            '//head/meta[@property="og:description"]/@content | //head/meta[@property="og:image"]/@content').extract()

        menu_list_group = [menu_list[i:i + 2] for i in range(0, len(menu_list), 2)]

        # 单例模式
        # ml = menu_list_group[0]
        # chapter_url_base = ml[0]
        # chapter_name = ml[1]
        #
        # # type(result) == "list"
        # # chapter_sort 即为我们自定义的章节顺序
        # result = re.findall('第(.*)章', chapter_name)
        # if not result:
        #     if ("序" in result) or ("楔子" in result):
        #         chapter_sort = 0
        #     else:
        #         chapter_sort = -1
        # else:
        #     chapter_sort = int(changeChineseNumToArab(result[0]))
        # print("chapter_sort", chapter_sort)
        #
        # meta = response.meta
        # article_title = meta.get("article_title", "")
        # chapter_url = response.meta["article_url"] + chapter_url_base
        # meta["chapter_url_base"] = chapter_url_base
        # meta["chapter_name"] = chapter_name
        # meta["article_title"] = article_title
        # meta['info'] = head_list[0][:511]
        # meta['thumb'] = head_list[1]
        # meta['chapter_sort'] = chapter_sort
        # # print(meta)
        # yield Request(chapter_url, meta=meta, callback=self.parse_content)
        # {'category_id': 1, 'category': '玄幻奇幻', 'depth': 2, 'download_timeout': 180.0,
        #  'download_slot': 'www.35kushu.com', 'download_latency': 0.3338916301727295,
        #  'article_url': 'https://www.35kushu.com/35zwhtml/70/70881/', 'title': '万古帝尊', 'is_full': 2, 'status': 1,
        #  'author': ' ', 'last_chapter': ' 第九百零八章 解决寄生虫', 'chapter_url_base': '4872854.html', 'chapter_name': '第一章 陆尘',
        #  'article_title': '',
        #  'info': '    亿载苦修凌绝顶，一朝不 慎落九幽;待吾重拾绝神体，不破苍天誓不休。    平定黑暗动乱，镇压诸天万族的巅峰强者龙帝神秘 陨落，重生于天幻王朝战王一脉。    查陨落之谜，铸无敌神体，誓要冲破天地束缚，且看陆尘如何逆天而行。',
        #  'thumb': 'http://www.35kushu.com/35zwimage/70/70881/70881s.jpg'}

        for index, ml in enumerate(menu_list_group):
            # print(ml)
            chapter_url_base = ml[0]
            chapter_name = ml[1]
            # # type(result) == "list"
            # # chapter_sort 即为我们自定义的章节顺序
            # print(chapter_name)
            count = chapter_name.count("第")
            re_str = (count - 1) * "." + "第(.*?)章"
            result = re.findall(re_str, chapter_name)
            # print(result)
            if not result:
                if ("序" in result) or ("楔子" in result):
                    chapter_sort = 0
                else:
                    chapter_sort = -1
            else:
                try:
                    chapter_sort = int(changeChineseNumToArab(result[0]))
                except:
                    break

            # print(chapter_sort, type(chapter_sort))
            meta = response.meta
            article_title = meta.get("article_title", "")
            chapter_url = response.meta["article_url"] + chapter_url_base
            meta["chapter_url_base"] = chapter_url_base
            meta["chapter_name"] = chapter_name
            meta["article_title"] = article_title
            meta['info'] = head_list[0][:511]
            meta['thumb'] = head_list[1]
            meta['chapter_sort'] = chapter_sort
            yield Request(chapter_url, meta=meta, callback=self.parse_content)

    def parse_content(self, response):
        content = response.xpath('//div[@id="main"]/div[@id="content"]/text()').extract()
        content = "<br><br>".join(content[1:])

        # print(response.meta)
        item = NovelsTagItem()
        item['article_title'] = response.meta["article_title"]
        item['chapter_name'] = response.meta["chapter_name"]
        item['chapter_content'] = content
        item['chapter_url_base'] = response.meta["chapter_url_base"]
        item['article_url'] = response.meta["article_url"]

        item['author'] = response.meta.get("author", "")
        item['category_id'] = response.meta.get("category_id", 0)
        item['category'] = response.meta.get("category", "")
        item['is_full'] = response.meta.get("is_full", 0)
        item['status'] = response.meta.get("status", 1)
        item['last_chapter'] = response.meta.get("last_chapter", " ")

        item['allowed_domain'] = self.allowed_domains[0]
        item['article_title'] = response.meta.get("article_title", "")
        item['article_url_base'] = response.meta.get("article_url_base", "")
        item['info'] = response.meta.get("info", "")
        item['thumb'] = response.meta.get("thumb")
        item['lastest_chapter_id'] = response.meta.get("lastest_chapter_id", "")
        item['chapter_sort'] = response.meta.get("chapter_sort", -1)
        item['words'] = response.meta.get("words", "")
        # print(item['chapter_sort'], type(item['chapter_sort']))
        # print(item['chapter_url_base'])

        # yield item
