from django.http import HttpResponse
from django.shortcuts import render_to_response, redirect
from django.utils.encoding import smart_str
from django.utils import simplejson

from debian.forms import SPARQLForm, SearchForm
from debian.services import SPARQLQueryProcessor, SPARQLQueryBuilder
from debian.services import FeedFinder
from debian.errors import SPARQLQueryProcessorError, UnexpectedSituationError
from debian.errors import SPARQLQueryBuilderError


def index(request):
    if request.method == 'GET':
        searchform = SearchForm()
        sparqlform = SPARQLForm()
        dict = {'search': searchform, 'sparql': sparqlform}
        return render_to_response('debian/search.html', dict)
    else:
        return HttpResponse("405 - Method not allowed", status=405)

def sparql(request):
    if request.method == 'POST':
        sparqlform = SPARQLForm(request.POST)
        
        if sparqlform.is_valid() is False:
            searchform = SearchForm()
            dict = {'search': searchform, 'sparql': sparqlform}
            return render_to_response('debian/search.html', dict)

        query = sparqlform.cleaned_data['ns'] + sparqlform.cleaned_data['query']
        processor = SPARQLQueryProcessor()
        try:
            processor.execute_query(smart_str(query))
        except SPARQLQueryProcessorError, e:
            return render_to_response('debian/error.html', {'reason': e})

        if sparqlform.cleaned_data['tojson_sparql'] is True:
            return HttpResponse(simplejson.dumps(processor.results), \
                mimetype="application/json")
        else:
            (variables, results) = processor.format_sparql_results()
            dict = {'variables': variables, 'results': results}
            return render_to_response('debian/results.html', dict)
    else:
        return HttpResponse("405 - Method not allowed", status=405)

def results(request):
    if request.method == 'POST':
        searchform = SearchForm(request.POST)

        if searchform.is_valid() is False:
            sparqlform = SPARQLForm()
            dict = {'search': searchform, 'sparql': sparqlform}
            return render_to_response('debian/search.html', dict)
        
        data = searchform.cleaned_data
        builder = SPARQLQueryBuilder()
        try:
            query = builder.create_query_from_form(data)
        except SPARQLQueryBuilderError, e:
            return render_to_response('debian/error.html', {'reason': e})

        processor = SPARQLQueryProcessor()
        try:
            processor.execute_sanitized_query(query)
        except SPARQLQueryProcessorError, e:
            return render_to_response('debian/error.html', {'reason': e})

        if builder.wants_json():
            return HttpResponse(simplejson.dumps(processor.results), \
                mimetype="application/json")
        elif builder.wants_html():
            if builder.source_search():
                results = processor.format_source_results()
            elif builder.binary_search():
                results = processor.format_binary_results()
            else:
                raise UnexpectedSituationError()
        else:
            raise UnexpectedSituationError()

        replydata = {'results': results, 'filter': data['filter']}
        replydata['query'] = query if data['showquery'] else None
        replydata['show_popcon'] = True if data['popcon'] else False

        if builder.source_search():
            return render_to_response('debian/source_results.html', replydata)
        elif builder.binary_search():
            return render_to_response('debian/binary_results.html', replydata)
        else:
            raise UnexpectedSituationError()
    else:
        return HttpResponse("405 - Method not allowed", status=405)

def news(request, source):
    if request.method == 'GET':
        finder = FeedFinder()

        try:
            feeds = finder.populate_feeds(source)
        except (SPARQLQueryProcessorError, SPARQLQueryBuilderError), e:
            return render_to_response('debian/error.html', {'reason': e})

        replydata = {'source': source, 'feeds': feeds}
        return render_to_response('debian/news.html', replydata)
    else:
        return HttpResponse("405 - Method not allowed", status=405)

def source_detail(request, source, version):
    if request.method == 'GET':
        builder = SPARQLQueryBuilder()
        try:
            query = builder.create_binaries_query(source, version)
        except SPARQLQueryBuilderError, e:
            return render_to_response('debian/error.html', {'reason': e})

        processor = SPARQLQueryProcessor()
        try:
            processor.execute_sanitized_query(query)
        except SPARQLQueryProcessorError, e:
            return render_to_response('debian/error.html', {'reason': e})

        results = processor.format_binary_results()
        return render_to_response('debian/binary_results.html', {'results': results})
    else:
        return HttpResponse("405 - Method not allowed", status=405)
