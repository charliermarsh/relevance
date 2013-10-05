from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib import auth
from django.contrib.auth import authenticate
from django.core.context_processors import csrf

from django.contrib.auth import authenticate, login, logout

import logging

from relevance_app.models import *
from relevance_app.helpers.facebookhelper import *
from relevance_app.helpers.newsfetcher import *
from relevance_app.helpers.likehelper import *
from relevance_app.helpers.likefilter_shubhro import *
from relevance_app.helpers.embedlyhelper import *
from relevance_app.helpers.diffbothelper import *

import urllib
import difflib
import json

from relevance_app.helpers.alchemyapi import AlchemyAPI

logging.basicConfig(level=logging.INFO)

def home(request):
    
    MEDIA_URL = settings.MEDIA_URL
    PAGE_TITLE = "Welcome to Relevance"
    
    return render_to_response('home.html',locals())

def connect(request):
    
    MEDIA_URL = settings.MEDIA_URL
    PAGE_TITLE = "Connect Facebook to Snocone"
    
    return render_to_response('connect.html',locals())

def fbchannelfile(request):
    
    MEDIA_URL = settings.MEDIA_URL
    return render_to_response('fbchannelfile.html',locals())

# logs the user in, and creates the account if haven't already
def ensure_user(request):

    MEDIA_URL = settings.MEDIA_URL
    
    # add the user to database if it is not already
    token = request.GET['token']
    fbhelper = FacebookHelper()
    fb_id,email = fbhelper.getUserFromToken(token, request.GET['fb_id'])
    
    # check whether this user is already in the system. If so, update the access token
    usernamefree = False
    try:
        user = User.objects.get(username=fb_id)
        profile = user.get_profile()
        profile.fb_token = token
        profile.save()
    except User.DoesNotExist:
        usernamefree = True
        
    if (usernamefree):
        
        user = User.objects.create_user(fb_id, email, fb_id)
        user.save()
        
        profile = user.get_profile()
        profile.fb_token = token
        profile.save()
        
        user = authenticate(username=fb_id, password=fb_id)
        login(request,user)
        fbhelper.import_friends(user)

    else:
        user = authenticate(username=fb_id, password=fb_id)
        login(request,user)

    message = "Connection success! " + user.username
    return render_to_response('message.html',locals())

@login_required
def query(request):

    MEDIA_URL = settings.MEDIA_URL
    
    user = request.user
    profile = user.get_profile()

    URL = request.GET["url"]
    
    lookup = "http://www.diffbot.com/api/article?token=59362348d4e230ba635d20eab5fd80e1&url="+URL
    f = urllib.urlopen(lookup)
    output = json.loads(f.read())
    text = output['text'].replace("\n"," ")

    alchemyapi = AlchemyAPI()
    result = alchemyapi.entities('url',URL)
    terms = [x["text"] for x in result["entities"]]

    

    fbpeople = []
    for term in terms:
        anyPeople = []
        results = profile.friends.filter(interests__name__iexact=term).distinct()
        for r in results:
            anyPeople.append(r.fb_id)
                
        if len(anyPeople) > 0:
            fbpeople.append((term,anyPeople))

    return render_to_response('query.html',locals())

@login_required
def friend_json(request, fb_id):
    
    user = request.user
    
    fbhelper = FacebookHelper()
    likehelper = LikeHelper()
    embedlyhelper = EmbedlyHelper()
    
    # Get this fb_person's likes from the database
    likes = []
    fbperson = Facebook_Person.objects.get(fb_id = fb_id)
    interests = fbperson.interests.filter()
    for interest in interests:
        likes.append((interest.name,interest.category))
    
    # fall back to FB API is friends not yet imported
    if len(interests) == 0:
        try:
            likes = fbhelper.getFriendLikes(user, fb_id)
        except:
            message = "FALSE"
            return render_to_response('intro/message.html',locals())
    
    dict = likehelper.createLikeDict(likes)
    articles = likehelper.likefilter(dict)
    
    # get the images for these articles
    for article in articles:
        
        try:
            results = embedlyhelper.get_terms_and_image(article.url)
            
            terms = results[0]
            imageData = results[1]
            summary = results[2]
            
            # put summary in
            article.summary = summary
            
            # put image data in
            article.image = imageData[0]
            article.imageWidth = imageData[1]
            article.imageHeight = imageData[2]
        
        except ValueError:
            continue
    
    
    
    return render_to_response('json/friend.html',locals())

@login_required
def newsfeed_json(request):
    
    user = request.user
    profile = user.get_profile()
    newsfetcher = NewsFetcher()
    diffbothelper = DiffbotHelper()
    embedlyhelper = EmbedlyHelper()
    
    if not profile.friends_imported:
        message = "FALSE"
        return render_to_response('intro/message.html',locals())
    
    items = []
    articles = newsfetcher.getHeadlinesAsArticles()
    for article in articles:
        
        try:
            item = Item()
            item.article = article
            
            results = embedlyhelper.get_terms_and_image(article.url)

            terms = results[0]
            imageData = results[1]
            summary = results[2]
                
            fbpeople = []
            for term in terms:

                anyPeople = []
                results = profile.friends.filter(interests__name__iexact=term).distinct()
                for r in results:
                    anyPeople.append(r.fb_id)
                        
                if len(anyPeople) > 0:
                    fbpeople.append((term,anyPeople))
                        
            item.fbpeople = fbpeople
        
            # put summary in
            item.article.summary = summary
            
            # put image data in
            item.article.image = imageData[0]
            item.article.imageWidth = imageData[1]
            item.article.imageHeight = imageData[2]
        
            items.append(item)
        except ValueError:
            continue

    return render_to_response('json/newsfeed.html',locals())