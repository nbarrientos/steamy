from django.http import HttpResponse
from django.shortcuts import render_to_response, redirect
from django.utils.encoding import smart_str

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
        query = f.cleaned_data['ns'] + f.cleaned_data['query']
        processor = SPARQLQueryProcessor()
        try:
            processor.execute_query(smart_str(query))
        except SyntaxError, e:
            return render_to_response('debian/error.html', {'reason': e.msg})

        (variables, results) = processor.format_sparql_results()
        dict = {'variables': variables, 'results': results}
        return render_to_response('debian/results.html', dict)
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

        processor.execute_sanitized_query(query)

        if builder.source_search:
            results = processor.format_source_results()
        elif builder.binary_search:
            results = processor.format_binary_results()
        else:
            raise Exception()

        replydata = {'results': results, 'filter': data['filter']}
        replydata['query'] = query if data['showquery'] else None
        replydata['show_popcon'] = True if data['popcon'] else False

        if builder.source_search:
            return render_to_response('debian/source_results.html', replydata)
        else:
            return render_to_response('debian/binary_results.html', replydata)
    else:
        return HttpResponse("405 - Method not allowed", status=405)
