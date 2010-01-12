from django.http import HttpResponse
from django.shortcuts import render_to_response, redirect

from debian.forms import SPARQLForm
from debian.services import SPARQLQueryProcessor, SPARQLQueryProcessorError

def index(request):
    return render_to_response('debian/index.html', {})

def sparql(request):
    if request.method == 'POST':
        f = SPARQLForm(request.POST)
        f.is_valid()
        
        processor = SPARQLQueryProcessor()
        try:
            htmlresults = processor.execute_query((f.cleaned_data['query']))
        except SPARQLQueryProcessorError, e:
            return render_to_response('debian/error.html', {'reason': e.reason})

        return render_to_response('debian/results.html', {'results': htmlresults})  # FIXME
    else:
        form = SPARQLForm()
        dict = {'form': form}
        return render_to_response('debian/sparql.html', dict)
