# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render
from django.urls import reverse
from django.http import HttpResponse,HttpResponseRedirect
from django.views.generic.base import View
from app_spider.models import APP_API,APP_TEMPLETE_ROOT
from mysite.settings import REDIS,SPIDER
import redis
import json
import requests
from datetime import datetime

search_client = None#Elasticsearch(hosts=["127.0.0.1"])
redis_cli = redis.StrictRedis(host=REDIS['HOST'], port=REDIS['PORT'], db=REDIS['DB'], password=REDIS['PASSWORD'])


# 网站爬虫内容展示页，对应index.html
def index(request):
    opt = request.GET.get('op', None)
    if opt is None:
        return HttpResponseRedirect(reverse('app_spider') + '?op=all')
    else:
        if opt == 'all':
            stats = json.loads(requests.get(url='http://'+SPIDER['HOST']+':8080/stats').text, encoding='utf-8')
            mongodb = []
            crawler = []
            for i in stats['mongodb']:
                mongodb.append({'name':i.keys()[0], 'count': i[i.keys()[0]]['count']})
            for i in stats['crawler']:
                crawler.append({'name':i.keys()[0], 'count': i[i.keys()[0]]})
            return HttpResponse(render(request, 'app_spider/index.html',{ \
                'title': '爬虫', \
                'op': opt, \
                'mongodb': mongodb, \
                'crawler': crawler, \
                }))
        elif opt == 'zhaopin':
            # res = json.loads(requests.get(url='http://' + SPIDER['HOST'] + ':8080/query').text, encoding='utf-8')
            return HttpResponse(render(request, 'app_spider/index.html', { \
                'title': '爬虫', \
                'op': opt, \
                }))
        elif opt == 'fangchan':
            # res = json.loads(requests.get(url='http://' + SPIDER['HOST'] + ':8080/query').text, encoding='utf-8')
            return HttpResponse(render(request, 'app_spider/index.html', { \
                'title': '爬虫', \
                'op': opt, \
                }))
        elif opt == 'hunlian':
            # res = json.loads(requests.get(url='http://' + SPIDER['HOST'] + ':8080/query').text, encoding='utf-8')
            return HttpResponse(render(request, 'app_spider/index.html', { \
                'title': '爬虫', \
                'op': opt, \
                }))


# 搜索功能首页，对应search.html
class IndexView(View):
    def get(self, request):
        topn_search = None#redis_cli.zrevrangebyscore("search_keywords_set", "+inf", "-inf", start=0, num=5)
        return render(request, "app_spider/search.html", {"topn_search":topn_search})


# 搜索建议，返回json数据
class SearchSuggest(View):
    def get(self, request):
        key_words = request.GET.get('s','')
        re_datas = []
        if key_words:
            s = None#ArticleType.search()
            s = s.suggest('my_suggest', key_words, completion={
                "field":"suggest", "fuzzy":{
                    "fuzziness":2
                },
                "size": 10
            })
            suggestions = s.execute_suggest()
            for match in suggestions.my_suggest[0].options:
                source = match._source
                re_datas.append(source["title"])
        return HttpResponse(json.dumps(re_datas), content_type="application/json")


# 搜索结果展示页，对应result.html
class SearchView(View):
    def get(self, request):
        key_words = request.GET.get("q","")
        s_type = request.GET.get("s_type", "article")

        redis_cli.zincrby("search_keywords_set", key_words)

        topn_search = redis_cli.zrevrangebyscore("search_keywords_set", "+inf", "-inf", start=0, num=5)
        page = request.GET.get("p", "1")
        try:
            page = int(page)
        except:
            page = 1

        jobbole_count = redis_cli.get("jobbole_count")
        start_time = datetime.now()
        response = search_client.search(
            index= "jobbole",
            body={
                "query":{
                    "multi_match":{
                        "query":key_words,
                        "fields":["tags", "title", "content"]
                    }
                },
                "from":(page-1)*10,
                "size":10,
                "highlight": {
                    "pre_tags": ['<span class="keyWord">'],
                    "post_tags": ['</span>'],
                    "fields": {
                        "title": {},
                        "content": {},
                    }
                }
            }
        )

        end_time = datetime.now()
        last_seconds = (end_time-start_time).total_seconds()
        total_nums = response["hits"]["total"]
        if (page%10) > 0:
            page_nums = int(total_nums/10) +1
        else:
            page_nums = int(total_nums/10)
        hit_list = []
        for hit in response["hits"]["hits"]:
            hit_dict = {}
            if "title" in hit["highlight"]:
                hit_dict["title"] = "".join(hit["highlight"]["title"])
            else:
                hit_dict["title"] = hit["_source"]["title"]
            if "content" in hit["highlight"]:
                hit_dict["content"] = "".join(hit["highlight"]["content"])[:500]
            else:
                hit_dict["content"] = hit["_source"]["content"][:500]

            hit_dict["create_date"] = hit["_source"]["create_date"]
            hit_dict["url"] = hit["_source"]["url"]
            hit_dict["score"] = hit["_score"]

            hit_list.append(hit_dict)

        return render(request, "app_spider/result.html", {"page":page,
                                                            "all_hits":hit_list,
                                                            "key_words":key_words,
                                                            "total_nums":total_nums,
                                                            "page_nums":page_nums,
                                                            "last_seconds":last_seconds,
                                                            "jobbole_count":jobbole_count,
                                                            "topn_search":topn_search})
