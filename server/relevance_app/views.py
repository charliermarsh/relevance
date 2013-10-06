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

    return render_to_response('home.html', locals())


def connect(request):

    MEDIA_URL = settings.MEDIA_URL
    PAGE_TITLE = "Connect Facebook to Snocone"

    return render_to_response('connect.html', locals())


def fbchannelfile(request):

    MEDIA_URL = settings.MEDIA_URL
    return render_to_response('fbchannelfile.html', locals())

# logs the user in, and creates the account if haven't already


def ensure_user(request):

    MEDIA_URL = settings.MEDIA_URL

    # add the user to database if it is not already
    token = request.GET['token']
    fbhelper = FacebookHelper()
    fb_id, email = fbhelper.getUserFromToken(token, request.GET['fb_id'])

    # check whether this user is already in the system. If so, update the
    # access token
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
        login(request, user)
        fbhelper.import_friends(user)

    else:
        user = authenticate(username=fb_id, password=fb_id)
        login(request, user)

    message = "Connection success! " + user.username
    return render_to_response('message.html', locals())


@login_required
def query(request):

    MEDIA_URL = settings.MEDIA_URL

    user = request.user
    profile = user.get_profile()

    URL = request.GET["url"]

    # lookup = "http://www.diffbot.com/api/article?token=59362348d4e230ba635d20eab5fd80e1&url="+URL
    # f = urllib.urlopen(lookup)
    # output = json.loads(f.read())
    # text = output['text'].replace("\n"," ")

    alchemyapi = AlchemyAPI()
    result = alchemyapi.entities('url', URL)
    terms = [x["text"].upper() for x in result["entities"]]

    pages = Facebook_Interest.objects.filter()
    page_names = [x.name for x in pages]
    page_names_upper = [x.upper() for x in page_names]
    page_lookup = {key: val for key, val in zip(page_names_upper, page_names)}

    response = []
    for term in terms:

        # anyPeople = []
        # results = profile.friends.filter(interests__name__iexact=term).distinct()
        # for r in results:
        #     anyPeople.append(r.fb_id)

        # if len(anyPeople) > 0:
        #     fbpeople.append((term,anyPeople))

        anyPeople = []
        matches = difflib.get_close_matches(term, page_names_upper, cutoff = 0.88)
        if not matches:
            continue
        pages_matched = [page_lookup[m] for m in matches]
        for p in pages_matched:
            results = profile.friends.filter(
                interests__name__iexact=p).distinct()
            for r in results:
                fb_person = Facebook_Person.objects.get(fb_id = r.fb_id)
                anyPeople.append((r.fb_id, fb_person.first_name))

            if len(anyPeople) > 0:
                response.append((p,list(set(anyPeople))))

    # remove duplicates in response
    already = []
    for i, item in enumerate(response):
        if item[0] not in already:
            already.append(item[0])
        else:
            del response[i]

    return render_to_response('query.html', locals())

def redirect(request):

    MEDIA_URL = settings.MEDIA_URL
    URL = request.GET["url"]
    destination = "http://localhost:8000/query/?url=%s" % URL
    return render_to_response('redirect.html',locals())

@login_required
def fbnetwork(request):
    MEDIA_URL = settings.MEDIA_URL
    URL = request.GET["url"]

    fbhelper = FacebookHelper()
    shares = json.dumps(fbhelper.getArticleInteractions(request.user, URL))
    #shares = shares = '{"shares": [{"to": [{"fbid": "826500443", "name": "Chris Murphy"}, {"fbid": "1092510133", "name": "Cara Hampton"}, {"fbid": "713159664", "name": "Danielle Mills"}], "from": {"fbid": "570166179", "name": "Julia Phillips"}, "interacted": [{"fbid": "826500443", "name": "Chris Murphy"}, {"fbid": "570166179", "name": "Julia Phillips"}]}]}'

    return render_to_response('fbnetwork.html', locals())
