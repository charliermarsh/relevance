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

    def importFriendsLinks(self, user):

        profile = user.get_profile()

        oauth_access_token = profile.fb_token
        graph = GraphAPI(oauth_access_token)

        fbpeople = profile.friends.filter(links_imported = False)
        total_queued = len(fbpeople)

        for index, fbperson in enumerate(fbpeople):

            query = "SELECT link_id, owner, url FROM link WHERE owner = %s LIMIT 10" % fbperson.fb_id
            oauth_access_token = profile.fb_token
            params = urllib.urlencode(
                {'q': query, 'access_token': oauth_access_token})
            url = "https://graph.facebook.com/fql?" + params
            data = urllib.urlopen(url)
            response = json.load(data)

            if "data" not in response.keys():
                continue

            for item in response['data']:
                fblink = Facebook_Link()
                fblink.fb_id = item["link_id"]
                fblink.url = item["url"]
                fblink.save()
                fblink.owner = [Facebook_Person.objects.get(fb_id = item["owner"])]
                fblink.save()


            fbperson.links_imported = True
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

    def getArticleInteractions_OLD(self, user, URL):
        profile = user.get_profile()

        # get request from FB Graph API
        def getData(URL):
            query = "SELECT permalink, tagged_ids, like_info, comments, actor_id, target_id FROM stream WHERE filter_key in (SELECT filter_key FROM stream_filter WHERE uid=me() AND type='newsfeed') AND strpos(attachment.href, '%s') >= 0 LIMIT 100" % URL
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

                targets = []
                if 'target_id' in e and e['target_id'] is not None:
                    targets.append(formatId(e['target_id']))
                if 'tagged_ids' in e and e['tagged_ids'] is not None:
                    targets += [formatId(i) for i in e['tagged_ids']]
                share['to'] = targets

                interacted = []
                if 'comment_list' in e['comments']:
                    for comment in e['comments']['comment_list']:
                        interacted.append(formatId(comment['fromid']))

                share['interacted'] = interacted

                return share

            try:
                parsed_data = {'shares': [parseEntry(e) for e in data['data']]}
                return parsed_data
            except:
                return None

        return parseData(getData(URL))

    def articleIsRelevant(self, URL):
        matches = Facebook_Link.objects.filter(url=URL)
        return bool(len(matches))

    def getArticleInteractions(self, user, URL):
        matches = Facebook_Link.objects.filter(url=URL)
        if not len(matches):
            return None
        fblink = matches[0]

        profile = user.get_profile()
        oauth_access_token = profile.fb_token

        graph = GraphAPI(oauth_access_token)

        data = graph.request(fblink.fb_id)
        if not data:
            return None

        liked = []
        commented = []

        if "likes" in data.keys():
            liked = [(x["id"],x["name"]) for x in data["likes"]["data"]]

        if "comments" in data.keys():
            commented = [(x["from"]["id"], x["from"]["name"]) for x in data["comments"]["data"]]
            print "HELLO!"
            print commented

        interacted = list(set(liked + commented))

        response = {'shares': [{"to": [], "from": {'fbid': str(data["from"]["id"]), 'name': data["from"]["name"]}, "interacted": [{'fbid': str(fb_id), 'name': name} for fb_id, name in interacted]}]}

        print response

        return response