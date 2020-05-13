# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

import os
import time
import pymysql
import redis

from .settings import REDIS_HOST, REDIS_PORT, REDIS_DB


class NovelsPipeline(object):
    def process_item(self, item, spider):
        return item


class NovelTagPipline(object):
    def __init__(self):
        # self.conn = pymysql.connect(host='127.0.0.1', user='root',
        #                             passwd='mima123', db='distributed_spider', charset='utf8')
        self.conn = pymysql.connect(host='47.56.7.182', user='root', port=3306,
                                    passwd='Fik2mcKWThRbEFyx', db='novel_spider_2.0', charset='utf8')
        self.cur = self.conn.cursor()
    #
        redis_pool = redis.ConnectionPool(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, decode_responses=True)  # redis缓存连接池
        self.redis = redis.StrictRedis(connection_pool=redis_pool, decode_responses=True)

    # 主要处理方法
    def process_item(self, item, spider):

        title = item.get('article_title', '')
        chapter_url_base = item.get('chapter_url_base', '')

        # 保存小说信息入库
        author = item.get('author', '')
        url = item.get('article_url', '')
        info = item.get('info', '')
        thumb = item.get('thumb', '')
        category_id = item.get('category_id', 0)
        category = item.get('category', 'default')
        # last_chapter = item.get('last_chapter', ' ')
        chapter_name = item.get('chapter_name', ' ')
        chapter_sort = item.get('chapter_sort', -1)
        is_full = item.get('is_full', 2)  # status 判断
        status = item.get('status', '')
        allowed_domain = item.get('allowed_domain', '')
        article_url_base = item.get('article_url_base', ' ')
        last_chapter = item.get('last_chapter', ' ')
        lastest_chapter_id = item.get('lastest_chapter_id', 0)
        words = item.get('words')

        temp_path_base = str(article_url_base)
        tp_list = temp_path_base.split("/")
        temp_path = tp_list[2]
        chapter_id = int(chapter_url_base[:-5])


        # 爬虫更新时间
        updated_at = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

        '''
        先写入缓存
        缓存到一定长度再写入mysql
        '''

        articles_dict = {
            "title": title,
            "pinyin": int(temp_path),
            "author": author,
            "url": url,
            "category_id": category_id,
            "category": category,
            "is_full": is_full,
            "status": status,
            "info": info,
            "thumb": thumb,
            "updated_at": updated_at,
            "last_chapter": last_chapter,
            "lastest_chapter_id": lastest_chapter_id,
            # "words": words
        }
        article_len = self.redis.hlen("acrticle_cache")
        if article_len < 10:
            self.redis.hmset("acrticle_cache", articles_dict)



        if not self.redis.hexists("articles_h", title):
            sql = "insert into articles(title, pinyin, author, url, category_id, category, " \
                  "is_full, `status`, info, thumb, updated_at, last_chapter, last_chapter_id) " \
                  "values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)  "
            try:
                self.cur.execute(sql, (title, int(temp_path), author, url, category_id, category,
                                       is_full, is_full, info, thumb, updated_at, last_chapter, int(lastest_chapter_id)))
                self.conn.commit()
                self.redis.hset("articles_h", title, -1)
            except Exception as e:
                if e.args[0] == 1062:
                    self.redis.hset("articles_h", title, -1)
                else:
                    print("articles_error", e)

        r_title_id = int(self.redis.hget("articles_h", title) or 0)
        if r_title_id not in (-1, 0, 1):
            article_id = r_title_id
        else:
            sql_id = "select id from articles where url =%s"
            self.cur.execute(sql_id, [url])
            result = self.cur.fetchone()
            article_id = result[0] if result else -1


        sql_chapter = "insert into articles_chapter(article_id, chapter_id, chapter_name, updated_at, chapter_sort, words) " \
                      "values(%s, %s, %s, %s, %s, %s)"
        try:
            if article_id != -1:
                self.cur.execute(sql_chapter, (article_id, chapter_id, chapter_name, updated_at, chapter_sort, words))
                self.conn.commit()
        except Exception as e:
            print("articles_chapter", e)


        # # linux路径
        # cur_path = "/mnt/d" + os.path.sep + allowed_domain
        cur_path = "/volume/novel_context" + os.path.sep + allowed_domain
        target_path = cur_path + os.path.sep + str(category_id) + os.path.sep + temp_path
        filename_path = cur_path + os.path.sep + str(category_id) + os.path.sep + temp_path + os.path.sep + \
                        str(chapter_url_base[:-5]) + '.txt'

        # print(target_path, filename_path)
        if not os.path.exists(target_path):
            os.makedirs(target_path)
        with open(filename_path, 'w', encoding='utf-8') as f:
            f.write(item['chapter_content'])
        return item

    def close_spider(self, spider):
        self.cur.close()
        self.conn.close()
