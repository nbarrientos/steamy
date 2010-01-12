from django.conf.urls.defaults import *

from debian.views import SearchWizard
from debian.forms import Step1Form, Step2Form

urlpatterns = patterns('debian.views',
    (r'^$', 'index'),
    (r'^sparql/$', 'sparql'),
    (r'^wizard/$', SearchWizard([Step1Form, Step2Form])),
)
