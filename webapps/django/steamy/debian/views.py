from django.http import HttpResponse
from django.shortcuts import render_to_response, redirect

from debian.models import Step1Form, step2_form_builder

def index(request):
  return render_to_response('debian/index.html', {})

def sparql(request):
  return render_to_response('debian/sparql.html', {})
