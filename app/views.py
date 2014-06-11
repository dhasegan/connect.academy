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

def about(request):
    context = {
        "page": "about",
    }
    return render(request, "pages/about.html", context)


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
    context['comments'] = Review.objects.all()

    return render(request, 'pages/comments.html', context)



@require_GET
def university_by_email(request):
# This function handles the asynchronous get requests sent by the javascript code,
# during user registration to confirm that the e-mail address (in the GET parameters)
# is available and valid.
# It returns a HTTP response with:
#   The name of the university (taken by the domain of the e-mail address) if it is found
#   "Exists" if a user with that e-mail address already exists
#   "NotFound" if a university with that domain is not found

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
# This function handles the asynchronous get requests sent by the javascript code,
# to check if the username (from the registration form) is valid 
# It returns:
#   "Username is required" if the username is empty
#   "Username exists" if a user with that username exists
#   "OK" if the username is available
    username = request.GET["username"]
    if username == "":
        return HttpResponse("Username is required")
    if jUser.objects.filter(username = username).count() > 0:
        return HttpResponse("Username exists")
    else:
        return HttpResponse("OK")

@require_GET
def validate_registration(request):
# This function handles the asynchronous get requests sent by the javascript code,
# to validate the username and the e-mail address on form submission
# It returns:
#   "Error" if the username or e-mail address are not valid
#   "OK" if they are both valid.
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
