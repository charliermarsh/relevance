"""
    Imports your Facebook friends' links!
"""

import os, sys
os.system("export DJANGO_SETTINGS_MODULE=relevance.settings")

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

if __name__ == "__main__":

    fb_id = sys.argv[1]

    user = authenticate(username=fb_id, password=fb_id)
    fbhelper = FacebookHelper()
    fbhelper.importFriendsLinks(user)
    message = "Links import complete."