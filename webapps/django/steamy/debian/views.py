from django.http import HttpResponse
from django.shortcuts import render_to_response, redirect

from debian.models import Step1Form, step2_form_builder

def index(request):
  request.session.set_test_cookie()
  return render_to_response('debian/index.html', {})

def step1(request):
  if request.session.test_cookie_worked():
    request.session.delete_test_cookie()
    request.session.flush()
    dict = {'form': Step1Form()}
    return render_to_response('debian/step1.html', dict)
  else:
    return HttpResponse("Please enable cookies and try again.")

def step2(request):
  if request.method == 'POST':
    f1 = Step1Form(request.POST)
    request.session.__setitem__("step1", f1.data)
    dict = {
      'form': step2_form_builder(request.session.__getitem__("step1")['pkgtype'])()}
    return render_to_response('debian/step2.html', dict)
  else:
    return HttpResponse("405: Method not allowed", status=405)

def sparql(request):
  return render_to_response('debian/sparql.html', {})
