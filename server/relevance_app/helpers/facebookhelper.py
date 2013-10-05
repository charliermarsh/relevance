from __future__ import with_statement
from urlparse import urlparse

from operator import itemgetter

from django.db import models
from django.contrib.auth.models import User
import datetime

# for fetching webdata
import urllib
import json
import re
import cgi
import urllib2
import cookielib

from relevance_app.helpers.facebook import *
from relevance_app.models import *

# for second version


class FacebookHelper():

    # returns the search results for searching the Graph API for the facebook
    # page
    def getUserFromToken(self, oauth_access_token, fb_id):

        graph = GraphAPI(oauth_access_token)
        results = graph.request(fb_id, args={'fields': 'email'})

        return results['id'], results['email']

    def import_friends(self, user):

        profile = user.get_profile()

        oauth_access_token = profile.fb_token
        graph = GraphAPI(oauth_access_token)

        results = graph.request(user.username, args={'fields': 'friends'})

        fbpeople = []
        for result in results['friends']['data']:

            fb_id = result['id']
            name = result['name']
            fbperson = self.ensureFacebookPerson(fb_id, name)
            profile.friends.add(fbperson)
            fbpeople.append(fbperson)

        return fbpeople

    def importFriendsLikes(self, user):

        profile = user.get_profile()

        oauth_access_token = profile.fb_token
        graph = GraphAPI(oauth_access_token)

        fbpeople = profile.friends.filter(likes_imported=False)
        total_queued = len(fbpeople)

        for index, fbperson in enumerate(fbpeople):

            results = graph.request(
                fbperson.fb_id, args={'fields': 'likes'})

            try:
                for result in results['likes']['data']:

                    fbinterest = self.ensureFacebookInterest(
                        result['id'], result['name'], result['category'])
                    self.ensureFacebookPersonHasInterest(fbperson, fbinterest)
            except:
                continue

            fbperson.likes_imported = True
            fbperson.save()

            print "%s of %s complete" % (index, total_queued)

        profile.friends_imported = True
        profile.save()

        return true

    def ensureFacebookPersonHasInterest(self, fbperson, fbinterest):

        fbperson.interests.add(fbinterest)

    def ensureFacebookPerson(self, fb_id, name = ""):

        try:
            fbperson = Facebook_Person.objects.get(fb_id=fb_id)
            exists = True
        except Facebook_Person.DoesNotExist:
            exists = False

        if not exists:

            fbperson = Facebook_Person()
            fbperson.fb_id = fb_id
            fbperson.first_name = name
            fbperson.save()

        return fbperson

    def ensureFacebookInterest(self, fb_id, name, category):

        try:
            fbinterest = Facebook_Interest.objects.get(fb_id=fb_id)
            exists = True
        except Facebook_Interest.DoesNotExist:
            exists = False

        if not exists:

            fbinterest = Facebook_Interest()
            fbinterest.fb_id = fb_id
            fbinterest.name = name
            fbinterest.category = category

            fbinterest.save()

        return fbinterest

    # returns a list of tuples of (like,category)
    def getFriendLikes(self, user, fb_id):

        profile = user.get_profile()

        oauth_access_token = profile.fb_token
        graph = GraphAPI(oauth_access_token)

        results = graph.request(fb_id, args={'fields': 'likes'})

        likes = []
        for r in results['likes']['data']:

            likes.append((r['name'], r['category']))

        return likes

    def getName(self, user, fb_id):
        profile = user.get_profile()

        oauth_access_token = profile.fb_token
        graph = GraphAPI(oauth_access_token)

        results = graph.request(fb_id, args={'fields': 'name'})

        return results['name']

    def getArticleInteractions(self, user, URL):
        profile = user.get_profile()

        # get request from FB Graph API
        def getData(URL):
            query = "SELECT permalink, like_info, comments, actor_id, target_id FROM stream WHERE filter_key in (SELECT filter_key FROM stream_filter WHERE uid=me() AND type='newsfeed') AND strpos(attachment.href, '%s') >= 0 LIMIT 100" % URL
            oauth_access_token = profile.fb_token
            params = urllib.urlencode(
                {'q': query, 'access_token': oauth_access_token})
            url = "https://graph.facebook.com/fql?" + params
            data = urllib.urlopen(url)
            result = json.load(data)
            return result

        def parseData(data):
            if not data:
                return None

            def formatId(id):
                return {'fbid': str(id), 'name': self.getName(user, str(id))}

            def parseEntry(e):
                share = {}

                share['from'] = formatId(e['actor_id'])

                if 'target_id' in e and e['target_id'] is not None:
                    share['to'] = formatId(e['target_id'])

                interacted = []
                if 'comment_list' in e['comments']:
                    for comment in e['comments']['comment_list']:
                        interacted.append(formatId(comment['fromid']))

                share['interacted'] = interacted

                return share

            parsed_data = {'shares': [parseEntry(e) for e in data['data']]}
            return parsed_data

        return parseData(getData(URL))
