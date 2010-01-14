from django.conf.urls.defaults import *
from django.conf import settings

urlpatterns = patterns('debian.views',
    (r'^$', 'index'),
    (r'^sparql/$', 'sparql'),
    (r'^search/$', 'search'),
)

if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
    )
