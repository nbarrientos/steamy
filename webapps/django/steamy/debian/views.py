from django.http import HttpResponse
from django.shortcuts import render_to_response, redirect

from debian.forms import SPARQLForm, SearchForm
from debian.services import SPARQLQueryProcessor, SPARQLQueryBuilder
from debian.errors import SPARQLQueryProcessorError, InvalidKeywordError


def index(request):
    return render_to_response('debian/index.html', {})

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
        form = SPARQLForm()
        dict = {'form': form}
        return render_to_response('debian/sparql.html', dict)

def search(request):
    if request.method == 'POST':
        f = SearchForm(request.POST)
        if f.is_valid():
            data = f.cleaned_data
        else:
            print f
            return render_to_response('debian/search.html', {'form': f})
        builder = SPARQLQueryBuilder(f.cleaned_data)
        processor = SPARQLQueryProcessor()
        try:
            query = builder.create_query()
        except InvalidKeywordError, e:
            return render_to_response("debian/error.html", {'reason': e.reason})

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
        form = SearchForm()
        dict = {'form': form}
        return render_to_response('debian/search.html', dict)
