from django.shortcuts import render, redirect
from django.http import Http404, HttpResponse
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.views.decorators.http import require_GET, require_POST

from app.models import *
from app.course_info import *
from app.context_processors import *


def welcome(request):
    if request.user and request.user.is_authenticated():
        return redirect('/home')

    context = {
        "page": "welcome",
    }
    return render(request, "pages/welcome_page.html", context)


@login_required
def home(request):
    context = {
        "page": "home",
    }

    courses = Course.objects.all()
    context = dict(context.items() + course_timeline_context(courses).items())
    return render(request, "pages/home.html", context)


@login_required
def all_comments(request):
    context = {
        'page': 'all_comments',
    }
    context['comments'] = Comment.objects.all()

    return render(request, 'pages/comments.html', context)


# This function takes an e-mail address and returns a HTTP Response with the name of the university that has the
# domain of the e-mail address. If it is not found, it returns HttpResponse("NotFound")
# It will be used to send AJAX requests from the welcome page during signup
@require_GET
def university_by_email(request):

    email = request.GET["email"]

    if jUser.objects.filter(email=email).count() > 0:
        return HttpResponse("Exists")

    try:
        _, domain = email.split("@")
    except ValueError as e:
        return HttpResponse("NotFound")

    universities = University.objects.filter(domains__name=domain)


    if not universities:
        return HttpResponse("NotFound")
    else:
        university = universities[0]
        return HttpResponse(university.name)

@require_GET
def check_username(request):
    username = request.GET["username"]
    if username == "":
        return HttpResponse("Username is too short")
    if jUser.objects.filter(username = username).count() > 0:
        return HttpResponse("Username exists")
    else:
        return HttpResponse("OK")

@require_GET
def validate_registration(request):
    username = request.GET['username']
    email = request.GET['email']

    try:
        _,domain = email.split('@')
    except ValueError:
        return HttpResponse("Error")

    if jUser.objects.filter(email=email).count() > 0:
        return HttpResponse("Error")
    elif jUser.objects.filter(username=username).count() > 0:
        return HttpResponse("Error")
    elif University.objects.filter(domains__name = domain).count() == 0:
        return HttpResponse("Error")
    else:
        return HttpResponse("OK")
