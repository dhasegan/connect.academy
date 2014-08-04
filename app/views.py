import json

from django.core.context_processors import csrf
from django.shortcuts import render, redirect
from django.http import Http404, HttpResponse
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.views.decorators.http import require_GET, require_POST

from app.models import *
from app.context_processors import *


def welcome(request):
    if request.user and request.user.is_authenticated():
        return redirect('/home')

    context = {
        "page": "welcome",
    }
    return render(request, "pages/welcome_page.html", context)


def about(request):
    context = {
        "page": "about",
    }
    return render(request, "pages/about.html", context)


@login_required
def dashboard(request):
    context = {
        'page': 'dashboard',
        'user_auth': request.user
    }

    context = dict(context.items() + dashboard_context(request).items())

    return render(request, "pages/dashboard.html", context)


@login_required
def all_comments(request):
    context = {
        'page': 'all_comments',
    }
    context['comments'] = Review.objects.all()

    return render(request, 'pages/comments.html', context)

def error_page(request, error_type):
    context = {
        'page': 'error_page',
        'error_type': error_type
    }

    return render(request, 'pages/error.html', context)
