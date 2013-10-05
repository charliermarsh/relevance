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
import cookielib, logging, json

import urlparse
from xml.etree.ElementTree import *

import formencode.validators as v

logging.basicConfig(level=logging.INFO)

class EmbedlyHelper():

    def get_terms_and_image(self, url):

        target = "http://api.embed.ly/1/extract?key=2777c1bd1f7349348e599d47636de6a8&url="+urllib.quote(url)
        f = urllib.urlopen(target)
        html = f.read()
        output = json.loads(html)

        terms = []
        try:
            for entity in output['entities']:
                terms.append(entity['name'])
        except:
            pass

        # get image

        # these are web sites that have terrible default images, so we should pick second one
        blackList = ["wsj.com", "yahoo.com", "bizjournals.com", "cbssports.com", "ft.com", "mercurynews.com", "abcnews.go.com", "nytimes.com"]
        index = 0

        if any(domain in url for domain in blackList):
            index = 1

        imageData = []
        try:
            imageData.append(output['images'][index]['url'])
            imageData.append(output['images'][index]['width'])
            imageData.append(output['images'][index]['height'])
        except:
            imageData.append("")
            imageData.append("0")
            imageData.append("0")
                
        # get summary
        summary = ""
        try:
            summary = output['description']
        except:
            pass

                
        return [terms, imageData, summary]