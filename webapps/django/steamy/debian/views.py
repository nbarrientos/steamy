from django.http import HttpResponse
from django.shortcuts import render_to_response

def index(request):
  return render_to_response('debian/index.html', {})

def step1(request):
  return render_to_response('debian/step1.html', {})

def sparql(request):
  return render_to_response('debian/sparql.html', {})
