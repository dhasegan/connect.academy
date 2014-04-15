from django.shortcuts import render, redirect
from django.http import Http404, HttpResponse
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.views.decorators.http import require_GET, require_POST

from app.models import *
from app.course_info import *
from app.context_processors import *
from app.helpers import *


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
    try:
        _, domain = email.split("@")
    except Exception as e:
        return HttpResponse("NotFound")

    universities = University.objects.filter(domains__name=domain)

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

    departments = Department.objects.filter(university__name=name).order_by('name')

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
