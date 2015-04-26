import uuid
from datetime import datetime
from django.shortcuts import render
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from pyrules import RuleContext, RuleEngine, RuleStore
from . import forms


def index(request):
    result = None
    logs = None
    if request.method == 'POST':
        form = forms.SampleForm(request.POST)
        if form.is_valid():
            context = RuleContext(form.cleaned_data)
            engine = RuleEngine()
            engine.execute(RuleStore().get_ruleset('Sample'), context)
            result = context.to_dict()
            logs = context._executed
    else:
        form = forms.SampleForm()
    return render(
        request, 'index.html', {'form': form, 'result': result, 'logs': logs})
