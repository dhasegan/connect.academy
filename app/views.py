# Shortcuts
from django.core.context_processors import csrf
from django.shortcuts import render, redirect, get_object_or_404, render_to_response
from django.http import Http404, HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.tokens import default_token_generator
from django.core.urlresolvers import reverse
from django.core.mail import send_mail
from django.template import RequestContext
from app.helpers import *
import hashlib
import string
import random

# Mimetypes for images
from mimetypes import guess_type

# App Models
from app.models import *
from app.course_info import *
from app.context_processor import *
from app.forms import *
from app.campusnet_login import *

def welcome(request):
    context = {
        "page": "welcome",
    }
    if user_authenticated(request):
        context['user_auth'] = request.user
        return redirect('/home')

    return render(request,"pages/welcome_page.html",context)

@login_required
def home(request):
    context = {
        "page": "home",
        'user_auth': user_authenticated(request)
    }
    # Get courses
    courses = Course.objects.all()
    context = dict(context.items() + course_timeline_context(courses).items())
    return render(request, "pages/home.html", context)

@login_required
def all_comments(request):
    context = {
        'page': 'all_comments',
        'user_auth': user_authenticated(request)
    }
    context['comments'] = Comment.objects.all()

    return render(request, 'pages/comments.html', context)


# This function takes an e-mail address and returns a HTTP Response with the name of the university that has the
# domain of the e-mail address. If it is not found, it returns HttpResponse("NotFound")
# It will be used to send AJAX requests from the welcome page during signup
def university_by_email(request):
    
    if request.method != "GET":
        raise Http404

    email = request.GET["email"]
    try:
        _, domain = email.split("@")
    except Exception as e:
        return HttpResponse("NotFound")


    universities = University.objects.filter(domains__name = domain)

    if len(universities) < 1:
        return HttpResponse("NotFound")

    university = universities[0]
    return HttpResponse(university.name)


# Takes the name of the university in the GET parameters (the key is 'name') and returns a <select> element filled
# with all the departments of that university as <option> elements
# To be used by the jQuery on welcome page (registration form)
def departments_by_university_name(request):
    if request.method != "GET":
        raise Http404

    name = request.GET["name"]

    departments = Department.objects.filter(university__name = name).order_by('name')

    if len(departments) < 1:
        return HttpResponse("<select class='form-control'><option value=''>Department</option></select>")

    return_string = """<select class='form-control' name = 'department'>
        <option value=''>Department</option>"""
    for department in departments:
        name = department.name
        d_id = department.id
        option = "<option value=%d> %s </option>" % (d_id, name)
        return_string += option
    return_string += "</select>"

    return HttpResponse(return_string)
