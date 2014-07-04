from django.core.context_processors import csrf
from django.shortcuts import render, redirect
from django.http import Http404, HttpResponse
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.views.decorators.http import require_GET, require_POST
from django.core.mail import send_mail

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
def home(request):
    context = {
        "page": "home",
    }

    courses = Course.objects.all()
    context = dict(context.items() + course_timeline_context(courses,request.user).items())
    return render(request, "pages/home.html", context)


@login_required
def my_courses(request):
    context = {
        'page': 'my_courses',
        'user_auth': request.user
    }
    user = request.user
    context['courses'] = []

    if user.user_type == USER_TYPE_STUDENT:
        registrations = StudentCourseRegistration.objects.filter(student=user)
        for reg in registrations:
            context['courses'].append({'course': reg.course, 'is_approved': reg.is_approved })
    
    elif user.user_type == USER_TYPE_PROFESSOR:
        registrations = ProfessorCourseRegistration.objects.filter(professor=user)
        for prof_reg in registrations: # for each professor registration
            course_dict = {'course':prof_reg.course, 
                           'is_approved': prof_reg.is_approved }
            if prof_reg.is_approved:
                course_dict['students'] = {'registered': [], 'pending': []}
                # for each student registration
                for student_reg in StudentCourseRegistration.objects.filter(course=prof_reg.course):
                    if student_reg.is_approved:
                        course_dict['students']['registered'].append(student_reg.student)
                    else:
                        course_dict['students']['pending'].append(student_reg.student)
                course_dict['documents'] = prof_reg.course.coursedocument_set.all()
                course_dict['homework'] = prof_reg.course.coursehomeworkrequest_set.all()
                course_dict['forum'] = None
                forums = prof_reg.course.forumcourse_set.all()
                if forums.count() == 1:
                    course_dict['forum'] = forums[0]
            context['courses'].append(course_dict)
        
    else:
        raise Http404

    return render(request, "pages/my_courses.html", context)


@login_required
@require_POST
def approve_student_registrations(request):
    context = {
        'page': 'approve_student_registrations',
    }
    context.update(csrf(request))

    #Make sure the logged in user is allowed to approve these registrations
    user = request.user
    course_id = request.POST['course']
    courses = Course.objects.filter(id=course_id)
    if courses is None:
        raise Http404
    else:
        course = courses[0]
    registrations = ProfessorCourseRegistration.objects.filter(course=course,professor=user,is_approved=True)
    if registrations is None:
        raise Http404
    
    # At this point we know that an approved professor of the course 
    # is attempting to approve sudent registrations

    # Approve each registration
    for key, val in request.POST.items():
        if 'student' in key:
            _,student_id = key.split('-')
            registrations = StudentCourseRegistration.objects.filter(course_id=course_id,
                student_id=student_id,
                is_approved = False)
            if registrations is not None:
                registration = registrations[0]
            else:
                raise Http404

            # Approve registration
            if val:
                registration.is_approved = True
                registration.save()

    return redirect('/my_courses')


@require_POST
@login_required
def send_mass_email(request):
    context = {
        'page': 'send_mass_email',
        'user_auth': request.user
    }
    context.update(csrf(request))

    #Make sure the logged in user is allowed to approve these registrations
    user = request.user
    subject = request.POST['subject']
    body = request.POST['email']
    to = []
    sender = "%s %s <%s>" % (user.first_name, user.last_name, user.email)
    for key, val in request.POST.items():
        if 'user' in key:
            _,user_id = key.split('-')
            users = jUser.objects.filter(id=user_id)
            if users is not None and val: #if user exists (users is not None) and checkbox was checked (val)
                email = users[0].email
                to.append(email)
    

    if len(to) > 0:
        send_mail(subject, body, sender, to, fail_silently=False)
        return HttpResponse("OK")
    else:
        return HttpResponse("Please select at least one recepient.")







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

