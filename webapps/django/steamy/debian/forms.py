from django.forms import widgets
from django import forms
from django.shortcuts import render_to_response
from django.contrib.formtools.wizard import FormWizard

from debian.config import SPARQL_PREFIXES, RES_BASEURI, ONT_URI 
from debian.services import SPARQLQueryBuilder, SPARQLQueryProcessor
from debian.errors import InvalidKeywordError

DIST_CHOICES = (
    ('ANY', 'any'),
    (RES_BASEURI+'/distribution/hamm', 'Hamm'),
    (RES_BASEURI+'/distribution/slink', 'Slink'),
    (RES_BASEURI+'/distribution/potato', 'Potato'),
    (RES_BASEURI+'/distribution/woody', 'Woody'),
    (RES_BASEURI+'/distribution/etch', 'Etch'),
    (RES_BASEURI+'/distribution/lenny', 'Lenny'),
)

PRIORITY_CHOICES = (
    ('ANY', 'any'),
    (ONT_URI+'required', 'required'),
    (ONT_URI+'important', 'important'),
    (ONT_URI+'standard', 'standard'),
    (ONT_URI+'optional', 'optional'),
    (ONT_URI+'extra', 'extra'),
)

AREA_CHOICES = (
    ('ANY', 'any'),
    (ONT_URI+'main', 'main'),
    (ONT_URI+'non-free', 'non-free'),
    (ONT_URI+'contrib', 'contrib'),
)

SEARCHTYPE_CHOICES = (
    ('SOURCE', 'Source package name'),
    ('BINARY', 'Binary package name only'),
    ('BINARYEXT', 'Binary package name and descriptions'),
)

MAINT_OPTS = (
    ('ALL', 'No restriction'),
    ('TEAM', 'Team-maintained packages'),
    ('DEBIAN', 'Maintainer emails matching "@debian.org$"'),
)

VERSION_OPTS = (
    ('ALL', 'No restriction'),
    ('NATIVE', 'Native packages'),
    ('NMU', 'NMued'),
    ('EPOCH', 'Epoched'),
)

VCS_OPTS = (
    ('ALL', 'No restriction'),
    ('SVN', 'Subversion'),
    ('GIT', 'Git'),
)

SORT_OPTS = (
    ('PACKAGE', 'Package name'),
    ('MAINTNAME', 'Maintainer name'),
    ('MAINTMAIL', 'Maintainer email'),
)

class Step1Form(forms.Form):
    distribution = forms.CharField(widget=widgets.Select(choices=DIST_CHOICES))
    area = forms.CharField(widget=widgets.Select(choices=AREA_CHOICES))
    searchtype = forms.CharField(initial="SOURCE", label="Search in:",\
        widget=widgets.RadioSelect(choices=SEARCHTYPE_CHOICES))
    filter = forms.CharField(required=False, max_length=30)

class Step2Form(forms.Form):
    priority = forms.CharField(widget=widgets.Select(choices=PRIORITY_CHOICES))
    maintainer = forms.CharField(initial="ALL", label="Maintainer restrictions:",\
        widget=widgets.RadioSelect(choices=MAINT_OPTS))
    version = forms.CharField(initial="ALL", label="Version restrictions:",\
        widget=widgets.RadioSelect(choices=VERSION_OPTS))
    vcs = forms.CharField(initial="ALL", label="Vcs restrictions:",\
        widget=widgets.RadioSelect(choices=VCS_OPTS))
    homepage = forms.BooleanField(label="Show homepage", required=False)
    sort = forms.CharField(initial="PACKAGE", label="Order by:",\
        widget=widgets.RadioSelect(choices=SORT_OPTS))

class SPARQLForm(forms.Form):
    default = SPARQL_PREFIXES + """
SELECT ?source ?maintainer
WHERE {
    ?source a deb:Source ;
      deb:maintainer ?maintainer ;
      deb:packageName "acl" .
}"""
    attrs = {'rows': '25', 'cols': '150'}
    query = forms.CharField(label=None, initial=default, widget=widgets.Textarea(attrs=attrs))

# Set custom templates
def get_template(self, step):
    return 'debian/wizard/step_%s.html' % step
FormWizard.get_template = get_template
