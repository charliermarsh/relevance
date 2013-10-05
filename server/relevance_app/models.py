from django.db import models
from django.contrib.auth.models import User
import datetime

from django.contrib.auth.models import User
from django.db.models.signals import post_save

# for fetching webdata
import urllib, re, cgi


class Facebook_Interest(models.Model):
    
    fb_id = models.CharField(max_length=400)
    name = models.CharField(max_length=400)
    category = models.CharField(max_length=400)

class Facebook_Person(models.Model):
    
    fb_id = models.CharField(max_length=400)
    first_name = models.CharField(max_length=400,null=True)
    last_name = models.CharField(max_length=400,null=True)
    current_location = models.CharField(max_length=400,null=True)
    hometown = models.CharField(max_length=400,null=True)
    interests = models.ManyToManyField(Facebook_Interest,null=True)

    likes_imported = models.BooleanField(default=False)

class UserProfile(models.Model):
    
    user = models.OneToOneField(User)

    first_name = models.CharField(max_length=400,null=True)
    last_name = models.CharField(max_length=400,null=True)

    current_location = models.CharField(max_length=400,null=True)
    hometown = models.CharField(max_length=400,null=True)

    fb_token = models.CharField(max_length=400,blank=True,null=True)
    friends_imported = models.BooleanField(default=False)
    friends = models.ManyToManyField(Facebook_Person,null=True)

def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

post_save.connect(create_user_profile, sender=User)