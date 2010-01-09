from django.conf.urls.defaults import *

urlpatterns = patterns('steamy.debian.views',
    (r'^$', 'index'),
    (r'^step1$', 'step1'),
    (r'^sparql$', 'sparql'),
)
