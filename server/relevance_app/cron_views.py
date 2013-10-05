from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib import auth
from django.contrib.auth import authenticate
from django.core.context_processors import csrf
from django.template import loader

from django.core.mail import send_mail, EmailMultiAlternatives

from django.contrib.auth import authenticate, login, logout

import logging
import datetime

from relevance_app.models import *
from relevance_app.helpers.facebookhelper import *
from relevance_app.helpers.newsfetcher import *
from relevance_app.helpers.embedlyhelper import *
from relevance_app.helpers.likehelper import *
from relevance_app.helpers.likefilter_shubhro import *

logging.basicConfig(level=logging.INFO)

def unimported(request):
    
    users = User.objects.filter(userprofile__friends_imported = False)
    
    return render_to_response('json/unimported.html',locals())

def importfriends(request, fb_id):
    
    user = authenticate(username=fb_id, password=fb_id)
    
    fbhelper = FacebookHelper()
    
    fbhelper.importFriendsLikes(user)
    
    message = "Likes import complete."
    return render_to_response('intro/connect_message.html',locals())

def headline(request):
    
    newsfetcher = NewsFetcher()
    embedlyhelper = EmbedlyHelper()
    
    current = datetime.datetime.now()
    expired = current - datetime.timedelta(days = 1) # only update headlines for users who haven't gotten anything in 24 hours
    users = User.objects.filter(userprofile__headline_sent__lte=(expired))
    users_with_friends = users.filter(userprofile__friends_imported = True)
    
    alerts = []
    articles = newsfetcher.getHeadlinesAsArticles()
    
    for cur_user in users_with_friends:
        for article in articles:
            try:
                profile = cur_user.get_profile()
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
            
                if len(fbpeople) > 0:
                    item = Item()
                    item.article = article
                    
                    item.fbpeople = fbpeople
                    
                    # put summary in
                    item.article.summary = summary
                    
                    # put image data in
                    item.article.image = imageData[0]
                    item.article.imageWidth = imageData[1]
                    item.article.imageHeight = imageData[2]
                    alerts.append([cur_user, item])
                    break
            
            except ValueError:
                continue

    for alert in alerts:
        # TODO: update the last_sent
        logging.info("Sent an alert")
        item = alert[1]
        subject, from_email, to = 'Snocone Alert', 'Snocone Support<drrelevance@gmail.com>', alert[0].email
        text_content = 'Please turn on HTML to view this email.'
        html_content = loader.render_to_string("alert.html", locals())
        msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
        msg.attach_alternative(html_content, "text/html")
        msg.send()

    message = "headlines sent!"
    return render_to_response('intro/message.html',locals())