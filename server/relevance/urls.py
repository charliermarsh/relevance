from django.conf.urls import patterns, include, url

from relevance_app.views import *


# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'relevance.views.home', name='home'),
    # url(r'^relevance/', include('relevance.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
    
                       
    # STATIC FILES
    (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
    (r'^favicon\.ico$', 'django.views.generic.simple.redirect_to', {'url': '/media/img/favicon.ico'}),
                       
    # INTRO VIEWS
    ('^$', home),
    ('^connect/$', connect),
    ('^fbchannelfile/$', fbchannelfile),
                       
    # APPLICATION VIEWS
    ('^ensure_user/$', ensure_user),
    ('^query/$', query),
    ('^fbnetwork/$', fbnetwork),
)
