from __future__ import with_statement
from urlparse import urlparse

from operator import itemgetter

from django.db import models
from django.contrib.auth.models import User
import datetime

# for fetching webdata
import urllib, re, cgi
import urllib2
import cookielib

from relevance_app.helpers.facebook import *
from relevance_app.models import *

# for second version
class FacebookHelper():
    
    # returns the search results for searching the Graph API for the facebook page
    def getUserFromToken(self, oauth_access_token, fb_id):
        
        graph = GraphAPI(oauth_access_token)
        results = graph.request(fb_id, args = {'fields':'email'})
        
        return results['id'],results['email']
    
    def import_friends(self, user):
        
        profile = user.get_profile()
        
        oauth_access_token = profile.fb_token
        graph = GraphAPI(oauth_access_token)
        
        results = graph.request(user.username, args = {'fields' : 'friends'})

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
    
        fbpeople = profile.friends.filter(likes_imported = False)
        total_queued = len(fbpeople)
        
        for index, fbperson in enumerate(fbpeople):
            
            results = graph.request(fbperson.fb_id, args = {'fields' : 'likes'})

            try:
                for result in results['likes']['data']:
            
                    fbinterest = self.ensureFacebookInterest(result['id'],result['name'],result['category'])
                    self.ensureFacebookPersonHasInterest(fbperson,fbinterest)
            except:
                continue
    
            fbperson.likes_imported = True
            fbperson.save()
                
            print "%s of %s complete" % (index, total_queued)

        profile.friends_imported = True
        profile.save()
    
        return true
    
    def ensureFacebookPersonHasInterest(self,fbperson,fbinterest):
                                                                                         
        fbperson.interests.add(fbinterest)

    def ensureFacebookPerson(self, fb_id, name = ""):

        try:
            fbperson = Facebook_Person.objects.get(fb_id = fb_id)
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
            fbinterest = Facebook_Interest.objects.get(fb_id = fb_id)
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
        
        results = graph.request(fb_id, args = {'fields':'likes'})
        
        likes = []
        for r in results['likes']['data']:
            
            likes.append((r['name'],r['category']))
        
        return likes