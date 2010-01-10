from django.db import models
from django.forms import widgets
from django import forms

DIST_CHOICES = (
    ('HAMM', 'Hamm'),
    ('SLINK', 'Slink'),
    ('POTATO', 'Potato'),
)

AREA_CHOICES = (
    ('MAIN', 'main'),
    ('NONFREE', 'non-free'),
    ('CONTRIB', 'contrib'),
)

PKGTYPE = (
    ('SOURCE', 'source'),
    ('BINARY', 'binary'),
    ('BOTH', 'both'),
)

class Step1(models.Model):
  distribution = models.CharField(max_length=10, choices=DIST_CHOICES)
  area = models.CharField(max_length=8, choices=AREA_CHOICES)
  pkgtype = models.CharField(max_length=8, choices=PKGTYPE)

class Step1Form(forms.ModelForm):
  pkgtype = forms.CharField(widget=widgets.RadioSelect(choices=PKGTYPE))

  class Meta:
    model = Step1

class Step2(models.Model):
  bin_package_name = models.CharField(max_length=30)
  src_package_name = models.CharField(max_length=30)

def step2_form_builder(pkgtype):
  if pkgtype == 'BOTH':
    fieldtuple = None
  elif pkgtype == 'BINARY':
    fieldtuple = ("bin_package_name",)
  elif pkgtype == 'SOURCE':
    fieldtuple = ("src_package_name",)

  class Step2Form(forms.ModelForm):
    class Meta:
      model = Step2
      fields = fieldtuple

  return Step2Form
