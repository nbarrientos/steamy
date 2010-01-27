# -*- coding: utf-8 -*-
#
# Nacho Barrientos Arias <nacho@debian.org>
#
# License: MIT

import re

from django.forms import widgets
from django import forms
from django.shortcuts import render_to_response
from django.utils.safestring import mark_safe

from debian.config import SPARQL_PREFIXES, RES_BASEURI, ONT_URI 
from debian.config import DEFAULT_QUERY
from debian.services import SPARQLQueryBuilder, SPARQLQueryProcessor


# Thanks: http://www.djangosnippets.org/snippets/316/
class HiddenBaseForm(forms.BaseForm):
    def as_hidden(self):
        """
        Returns this form rendered entirely as hidden fields.
        """
        return mark_safe(u'\n'.join(forms.forms.BoundField(self, field, name).as_hidden() \
                                    for name, field in self.fields.items()))
    as_hidden.needs_autoescape = True


DIST_OPTS = (
    ('ANY', 'any'),
    (RES_BASEURI+'/distribution/hamm', 'Hamm'),
    (RES_BASEURI+'/distribution/slink', 'Slink'),
    (RES_BASEURI+'/distribution/potato', 'Potato'),
    (RES_BASEURI+'/distribution/woody', 'Woody'),
    (RES_BASEURI+'/distribution/sarge', 'Sarge'),
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
    ('SOURCE', 'Source package names'),
    ('BINARY', 'Binary package names'),
    ('BINARYEXT', 'Binary package names and descriptions'),
)

MAINT_OPTS = (
    ('ALL', 'No restriction'),
    ('TEAM', 'Team-maintained packages'),
    ('DEBIAN', 'Only maintainers with @debian.org address'),
    ('QA', 'Maintainer is Debian Quality Assurance Group'),
    ('CUSTOM', 'Custom filter (use text field below to set one)'),
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
    ('SVN', 'Subversion'),
    ('GIT', 'Git'),
    ('CVS', 'Cvs'),
    ('HG', 'Mercurial'),
)

SORT_OPTS = (
    ('PACKAGE', 'Package name'),
    ('MAINTMAIL', 'Maintainer email'),
)


class SearchForm(forms.Form, HiddenBaseForm):
    distribution = forms.ChoiceField(widget=widgets.Select, choices=DIST_OPTS)
    area = forms.ChoiceField(widget=widgets.Select, choices=AREA_OPTS)
    searchtype = forms.ChoiceField(initial="SOURCE", label="Search in:",\
        widget=widgets.RadioSelect, choices=SEARCHTYPE_OPTS)
    filter = forms.RegexField(regex=re.compile(r"^[-a-zA-Z0-9+.]*$"),\
        max_length=30, required=False)
    exactmatch = forms.BooleanField(required=False)
    priority = forms.ChoiceField(choices=PRIORITY_OPTS)
    maintainer = forms.ChoiceField(initial="ALL",\
        widget=widgets.RadioSelect, choices=MAINT_OPTS)
    comaintainer = forms.ChoiceField(initial="ALL",\
        widget=widgets.RadioSelect, choices=COMAINT_OPTS)
    version = forms.MultipleChoiceField(\
        widget=widgets.CheckboxSelectMultiple, choices=VERSION_OPTS,\
        required=False)
    vcs = forms.MultipleChoiceField(widget=widgets.CheckboxSelectMultiple,\
        choices=VCS_OPTS, required=False)
    essential = forms.BooleanField(required=False)
    buildessential = forms.BooleanField(required=False)
    dmuploadallowed = forms.BooleanField(required=False)
    homepage = forms.BooleanField(required=False)
    sort = forms.ChoiceField(initial="PACKAGE",\
        widget=widgets.RadioSelect, choices=SORT_OPTS)
    showquery = forms.BooleanField(required=False)
    popcon = forms.BooleanField(required=False)
    section = forms.RegexField(regex=re.compile(r"^[a-zA-Z]*$"),\
        max_length=20, required=False)
    maintainerfilter = forms.RegexField(regex=re.compile(r"^[-\w@.+]*$"),\
        max_length=40, required=False)
    tojson = forms.BooleanField(required=False)

class SPARQLForm(forms.Form):
    ns = forms.CharField(required=False, initial=SPARQL_PREFIXES, widget=widgets.Textarea())
    query = forms.CharField(initial=DEFAULT_QUERY, widget=widgets.Textarea())
    tojson_sparql = forms.BooleanField(required=False)
