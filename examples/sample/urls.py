from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns(
    '',
    url(r'^$', 'examples.sample.sampleapp.views.index', name='index'),
    url(r'^', include('app.urls')),
)
