import re

from django.forms import widgets
from django import forms
from django.shortcuts import render_to_response

from debian.config import SPARQL_PREFIXES, RES_BASEURI, ONT_URI 
from debian.services import SPARQLQueryBuilder, SPARQLQueryProcessor
from debian.errors import InvalidKeywordError

DIST_OPTS = (
    ('ANY', 'any'),
    (RES_BASEURI+'/distribution/hamm', 'Hamm'),
    (RES_BASEURI+'/distribution/slink', 'Slink'),
    (RES_BASEURI+'/distribution/potato', 'Potato'),
    (RES_BASEURI+'/distribution/woody', 'Woody'),
    (RES_BASEURI+'/distribution/etch', 'Etch'),
    (RES_BASEURI+'/distribution/lenny', 'Lenny'),
)

PRIORITY_OPTS = (
    ('ANY', 'any'),
    (ONT_URI+'required', 'required'),
    (ONT_URI+'important', 'important'),
    (ONT_URI+'standard', 'standard'),
    (ONT_URI+'optional', 'optional'),
    (ONT_URI+'extra', 'extra'),
)

AREA_OPTS = (
    ('ANY', 'any'),
    (ONT_URI+'main', 'main'),
    (ONT_URI+'non-free', 'non-free'),
    (ONT_URI+'contrib', 'contrib'),
)

SEARCHTYPE_OPTS = (
    ('SOURCE', 'Source package name'),
    ('BINARY', 'Binary package name only'),
    ('BINARYEXT', 'Binary package name and descriptions'),
)

MAINT_OPTS = (
    ('ALL', 'No restriction'),
    ('TEAM', 'Team-maintained packages'),
    ('DEBIAN', 'Only maintainers with @debian.org address'),
    ('QA', 'Maintainer is Debian Quality Assurance Group'),
)

COMAINT_OPTS = (
    ('ALL', 'No restriction'),
    ('WITH', 'With comantainers'),
    ('WITHOUT', 'Without them'),
)

VERSION_OPTS = (
    ('NATIVE', 'Native'),
    ('NMU', 'NMUed'),
    ('EPOCH', 'With epoch'),
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

class SearchForm(forms.Form):
    distribution = forms.ChoiceField(widget=widgets.Select, choices=DIST_OPTS)
    area = forms.ChoiceField(widget=widgets.Select, choices=AREA_OPTS)
    searchtype = forms.ChoiceField(initial="SOURCE", label="Search in:",\
        widget=widgets.RadioSelect, choices=SEARCHTYPE_OPTS)
    filter = forms.RegexField(regex=re.compile(r"^[-a-zA-Z0-9+.]*$"),\
        max_length=30, required=False)
    priority = forms.ChoiceField(choices=PRIORITY_OPTS)
    maintainer = forms.ChoiceField(initial="ALL",\
        widget=widgets.RadioSelect, choices=MAINT_OPTS)
    comaintainer = forms.ChoiceField(initial="ALL",\
        widget=widgets.RadioSelect, choices=COMAINT_OPTS)
    version = forms.MultipleChoiceField(initial="ALL",\
        widget=widgets.CheckboxSelectMultiple, choices=VERSION_OPTS,\
        required=False)
    vcs = forms.ChoiceField(initial="ALL",\
        widget=widgets.RadioSelect, choices=VCS_OPTS)
    homepage = forms.BooleanField(required=False)
    sort = forms.ChoiceField(initial="PACKAGE",\
        widget=widgets.RadioSelect, choices=SORT_OPTS)
    showquery = forms.BooleanField(required=False)
    section = forms.RegexField(regex=re.compile(r"^[a-zA-Z]*$"),\
        max_length=20, required=False)

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
