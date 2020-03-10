# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class NovelsItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class NovelsTagItem(scrapy.Item):
    # 公用
    title = scrapy.Field()              # 小说标题

    # 入文件用
    chapter_name = scrapy.Field()       # 小说章节名字
    chapter_content = scrapy.Field()    # 小说章节内容
    chapter_url_base = scrapy.Field()   # 小说base url (eg:120202.html)

    # 入mysql
    article_url = scrapy.Field()        # 小说的链接
    lastest_url = scrapy.Field()        # 最新一章的章节链接
    last_chapter = scrapy.Field()       # 最新一章的章节标题
    author = scrapy.Field()             # 小说作者
    updated_at = scrapy.Field()         # 更新时间
    status = scrapy.Field()             # 状态
    is_full = scrapy.Field()            # 连载状态
    category_id = scrapy.Field()        # 类型id
    category = scrapy.Field()           # 类型文字

    allowed_domain = scrapy.Field()     # 域名
    article_title = scrapy.Field()
    article_url_base = scrapy.Field()

    info = scrapy.Field()
    thumb = scrapy.Field()
    lastest_chapter_id = scrapy.Field()

    chapter_sort = scrapy.Field()
    words = scrapy.Field()




