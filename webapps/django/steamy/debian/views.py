from django.http import HttpResponse
from django.shortcuts import render_to_response, redirect

from debian.forms import SPARQLForm, SearchForm
from debian.services import SPARQLQueryProcessor, SPARQLQueryBuilder
from debian.errors import SPARQLQueryProcessorError, InvalidKeywordError


def index(request):
    searchform = SearchForm()
    sparqlform = SPARQLForm()
    dict = {'search': searchform, 'sparql': sparqlform}
    return render_to_response('debian/search.html', dict)

def sparql(request):
    if request.method == 'POST':
        f = SPARQLForm(request.POST)
        f.is_valid()
        
        processor = SPARQLQueryProcessor()
        try:
            processor.execute_query((f.cleaned_data['query']))
        except SyntaxError, e:
            return render_to_response('debian/error.html', {'reason': e.msg})

        htmlresults = processor.format_htmltable()
        return render_to_response('debian/results.html', {'results': htmlresults})
    else:
        return HttpResponse("405 - Method not allowed", status=405)

def results(request):
    if request.method == 'POST':
        searchform = SearchForm(request.POST)
        sparqlform = SPARQLForm()
        if searchform.is_valid():
            data = searchform.cleaned_data
        else:
            dict = {'search': searchform, 'sparql': sparqlform}
            return render_to_response('debian/search.html', dict)
        builder = SPARQLQueryBuilder(data)
        processor = SPARQLQueryProcessor()
        query = builder.create_query()

        print query # FIXME
        processor.execute_sanitized_query(query)
        if builder.source_search:
            results = processor.format_source_results()
            replydata = {'results': results, 'filter': data['filter']}
            replydata['query'] = query if data['showquery'] else None
            return render_to_response('debian/source_results.html', replydata)
        else:
            results = processor.format_source_results()
    else:
        return HttpResponse("405 - Method not allowed", status=405)
