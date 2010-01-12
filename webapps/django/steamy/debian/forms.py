from django.forms import widgets
from django import forms
from django.shortcuts import render_to_response
from django.contrib.formtools.wizard import FormWizard

from debian.config import SPARQL_PREFIXES, RES_BASEURI, ONT_URI 
from debian.services import SPARQLQueryBuilder, SPARQLQueryProcessor

DIST_CHOICES = (
    ('any', 'any'),
    (RES_BASEURI+'/distribution/hamm', 'Hamm'),
    (RES_BASEURI+'/distribution/slink', 'Slink'),
    (RES_BASEURI+'/distribution/potato', 'Potato'),
    (RES_BASEURI+'/distribution/woody', 'Woody'),
    (RES_BASEURI+'/distribution/etch', 'Etch'),
    (RES_BASEURI+'/distribution/lenny', 'Lenny'),
)

AREA_CHOICES = (
    ('any', 'any'),
    (ONT_URI+'main', 'main'),
    (ONT_URI+'non-free', 'non-free'),
    (ONT_URI+'contrib', 'contrib'),
)

SEARCHTYPE_CHOICES = (
    ('BINARY', 'Binary package name only'),
    ('BINARYEXT', 'Binary package name and descriptions'),
    ('SOURCE', 'Source package name'),
)

class Step1Form(forms.Form):
    distribution = forms.CharField(widget=widgets.Select(choices=DIST_CHOICES))
    area = forms.CharField(widget=widgets.Select(choices=AREA_CHOICES))
    searchtype = forms.CharField(label="Search in:",\
        widget=widgets.RadioSelect(choices=SEARCHTYPE_CHOICES))

class Step2Form(forms.Form):
    filter = forms.CharField(max_length=30)

class SPARQLForm(forms.Form):
    default = SPARQL_PREFIXES + """
SELECT ?s
WHERE {
    ?s a deb:Source
}"""
    attrs = {'rows': '25', 'cols': '150'}
    query = forms.CharField(label=None, initial=default, widget=widgets.Textarea(attrs=attrs))

class SearchWizard(FormWizard):
    def done(self, request, form_list):
        data = {}
        for form in form_list:
            data.update(form.cleaned_data)
        print data # FIXME
        builder = SPARQLQueryBuilder(data)
        processor = SPARQLQueryProcessor()
        # FIXME
        htmlresults = processor.execute_sanitized_query(builder.create_query())
        return render_to_response('debian/results.html', {
            'results': htmlresults,
        })

# Set custom templates
def get_template(self, step):
    return 'debian/wizard/step_%s.html' % step
FormWizard.get_template = get_template
