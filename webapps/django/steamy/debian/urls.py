from django.conf.urls.defaults import *
from django.conf import settings

urlpatterns = patterns('debian.views',
    (r'^$', 'index'),
    (r'^sparql/$', 'sparql'),
    (r'^results/$', 'results'),
    (r'^results/news/$', 'allnews'),
    (r'^news/(?P<source>[^/ ]+)/$', 'news'),
    (r'^binaries/(?P<source>[^/ ]+)/(?P<version>[^/ ]+)/$', 'source_detail'),
)

if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
    )
