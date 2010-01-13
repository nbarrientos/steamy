from django.http import HttpResponse
from django.shortcuts import render_to_response, redirect
from django.contrib.formtools.wizard import FormWizard

from debian.forms import SPARQLForm
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
        except SPARQLQueryProcessorError, e:
            return render_to_response('debian/error.html', {'reason': e.reason})

        htmlresults = processor.format_htmltable()
        return render_to_response('debian/results.html', {'results': htmlresults})
    else:
        form = SPARQLForm()
        dict = {'form': form}
        return render_to_response('debian/sparql.html', dict)

class SearchWizard(FormWizard):
    def done(self, request, form_list):
        data = {}
        for form in form_list:
            data.update(form.cleaned_data)
        print data # FIXME
        builder = SPARQLQueryBuilder(data)
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
            return render_to_response('debian/binary_results.html', {'results': results})
