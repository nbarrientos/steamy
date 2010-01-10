from django.forms import widgets
from django import forms
from django.shortcuts import render_to_response
from django.contrib.formtools.wizard import FormWizard

DIST_CHOICES = (
    ('ANY', 'any'),
    ('HAMM', 'Hamm'),
    ('SLINK', 'Slink'),
    ('POTATO', 'Potato'),
)

AREA_CHOICES = (
    ('ANY', 'any'),
    ('MAIN', 'main'),
    ('NONFREE', 'non-free'),
    ('CONTRIB', 'contrib'),
)

PKGTYPE_CHOICES = (
    ('ANY', 'any'),
    ('SOURCE', 'source'),
    ('BINARY', 'binary'),
)

class Step1Form(forms.Form):
    distribution = forms.CharField(widget=widgets.Select(choices=DIST_CHOICES))
    area = forms.CharField(widget=widgets.Select(choices=AREA_CHOICES))
    pkgtype = forms.CharField(widget=widgets.RadioSelect(choices=PKGTYPE_CHOICES))

class Step2Form(forms.Form):
    filter = forms.CharField(max_length=30)
    description = forms.BooleanField(required=False)

class SPARQLForm(forms.Form):
    default = """
PREFIX deb:<http://idi.fundacionctic.org/steamy/debian.owl#>
PREFIX rdf:<http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs:<http://www.w3.org/2000/01/rdf-schema#>
PREFIX nfo:<http://www.semanticdesktop.org/ontologies/2007/03/22/nfo#>
PREFIX tag:<http://www.holygoat.co.uk/owl/redwood/0.1/tags#>
PREFIX foaf:<http://xmlns.com/foaf/0.1/#>
PREFIX doap:<http://usefulinc.com/ns/doap#>

SELECT ?s
WHERE {
    ?s a deb:Source
} 
LIMIT 10"""
    attrs = {'rows': '25', 'cols': '150'}
    query = forms.CharField(label=None, initial=default, widget=widgets.Textarea(attrs=attrs))

class SearchWizard(FormWizard):
    def done(self, request, form_list):
        # Process results
        return render_to_response('debian/results.html', {
            'form_data': [form.cleaned_data for form in form_list],
        })

# Set custom templates
def get_template(self, step):
    return 'debian/wizard/step_%s.html' % step
FormWizard.get_template = get_template
