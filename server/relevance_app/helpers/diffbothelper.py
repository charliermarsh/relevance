# for converting URL to domain
from __future__ import with_statement
from urlparse import urlparse

from django.db import models
from django.contrib.auth.models import User
import datetime
import hashlib
import difflib

# for fetching webdata
import urllib, re, cgi
import urllib2
import cookielib, logging

import urlparse
from xml.etree.ElementTree import *

import formencode.validators as v

logging.basicConfig(level=logging.INFO)

class DiffbotHelper():

    def fetch_stuff(self, url, params, method):
        params = urllib.urlencode(params)
        if method=='POST':
            f = urllib.urlopen(url, params)
        else:
            f = urllib.urlopen(url+'?'+params)
        return (f.read(), f.code)
    
    def get_diffbot_page_id(self, url):
        
        logging.info(url)
        
        content, response_code = self.fetch_stuff('http://www.diffbot.com/api/add', {'token': '59362348d4e230ba635d20eab5fd80e1', 'url': url}, 'POST')
        logging.info(content)
        tree = fromstring(content)

        return tree.get('id')

    # DOESN'T WORK, DIFFBOT RETURNS ERROR
    def get_body(self, url):
        
        diffbot_page_id = self.get_diffbot_page_id(url)
        
        f = urllib.urlopen("http://www.diffbot.com/api/dfs/dml/archive?id="+diffbot_page_id+"&token=59362348d4e230ba635d20eab5fd80e1")
        html = f.read()
        #logging.info(html)
        tree = fromstring(html)
        
        
        #logging.info("HELLO")
        #logging.info(tree)
        
        #for item_raw in tree.findall("dml/item"):
        return true