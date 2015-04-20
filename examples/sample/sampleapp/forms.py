from django import forms
from django.contrib.auth.models import User


class SampleForm(forms.Form):
    first = forms.IntegerField()
    second = forms.IntegerField()
