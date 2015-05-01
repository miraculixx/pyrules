from django.conf.urls import patterns, include, url
from django.contrib import admin
from pyrules.api.config import pr_v1

admin.autodiscover()

urlpatterns = patterns(
    '',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^api/', include(pr_v1.urls))
)
