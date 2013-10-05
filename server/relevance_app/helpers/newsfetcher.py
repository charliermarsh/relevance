# for converting URL to domain
from __future__ import with_statement
from urlparse import urlparse

from django.db import models
from django.contrib.auth.models import User
import datetime

import cookielib, logging

import urllib, urllib2, base64
import json, feedparser

from relevance_app.helpers.globals import *

logging.basicConfig(level=logging.INFO)


from HTMLParser import HTMLParser

class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return ' '.join(self.fed)

def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()

# for second version
class NewsFetcher():

    def getTopArticleForTopic(self, topic):
        
        username = ""
        password = "r3z4veqyIgw+/uL5wv57yh4R41+kYGKKPxXYb8A5eBw="
        
        request = urllib2.Request("https://api.datamarket.azure.com/Data.ashx/Bing/Search/News?Query=%27"+urllib.quote(topic)+"%27&$top=15&$format=JSON&Market=%27en-US%27")
        base64string = base64.encodestring('%s:%s' % (username, password)).replace('\n', '')
        request.add_header("Authorization", "Basic %s" % base64string)   
        response = urllib2.urlopen(request)
        
        raw_response_read = response.read()
        
        output = json.loads(raw_response_read)
        
        #logging.info(raw_response_read)

        oldest_time = None
        
        try:
            item = output['d']['results'][0]
            
            # parse the date into datetime object before sending
            date_published = datetime.datetime.strptime(item['Date'], '%Y-%m-%dT%H:%M:%SZ') # 2012-06-15T20:46:55Z
            
            return Article(item['Title'], item['Description'], item['Url'], date = date_published, topic = topic.replace("\"",""))
        except:
            return False


    def getHeadlinesAsArticles(self):

        
        # gets rss for top headlines from google news

        url = "http://news.google.com/news?pz=1&cf=all&ned=us&hl=en&output=rss"

        d = feedparser.parse(url)

        articles = []
        for item in d.entries:
            
            title = item.title
            desc = strip_tags(item.description)
            url = item.link.split("&url=")[-1]
            date_published = item.updated #datetime.datetime.strptime(item.cloud['pubdate'], '%a, %d %b %Y %H:%M:%S %Z') #Wed, 17 Apr 2013 11:05:28 GMT
            article = Article(title, desc, url, date = date_published, topic = "")
            articles.append(article)
        
        return articles