from mimetypes import guess_type
import hashlib
import string
import random
import datetime

from django.core.context_processors import csrf
from django.shortcuts import render, redirect, get_object_or_404, render_to_response
from django.http import Http404, HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.tokens import default_token_generator
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.views.decorators.http import require_GET, require_POST
#from django.db import transaction
#import reversion

from app.models import *
from app.context_processors import *
from app.wiki.forms import *


#@transaction.atomic()
#@reversion.create_revision()
@login_required
def edit_wiki_page(request,slug):
    context = {
        "page":"edit_wiki_page",
        'slug': slug,
    }
    course = Course.objects.get(slug=slug)
    wikis = course.wiki.all()
    if len(wikis) > 0:
    	wiki = wikis[0]
    	context['course'] = course
       	context['content'] = wiki.content
    	
    else:
    	context['course'] = course
        professors = []
        for reg in ProfessorCourseRegistration.objects.filter(course=course,is_approved=True):
            professors.append(reg.professor)
        context['content'] = render_to_string('objects/wiki/default_content.html',{
                'STATIC_URL': "/static/",
                'course': course,
                'professors': professors,
                'registered_students': StudentCourseRegistration.objects.filter(course=course,
                                                                is_approved=True).count(),
                'pending_students': StudentCourseRegistration.objects.filter(course=course,
                                                                is_approved=False).count()
            })
    	
    return render(request,"pages/edit_wiki_page.html",context)

    

#@transaction.atomic()
#@reversion.create_revision()
@require_POST
@login_required
def save_wiki_page(request,slug):
    context = {
        "page":"edit_wiki_page", # it will be rendered on edit_wiki_page
        "slug": slug,
    }
    context.update(csrf(request))
    course = Course.objects.get(slug=slug)
    user = request.user

    if course is not None and user.university != course.university:
        raise Http404

    if user.university != course.university:
        raise Http404

    modified_on = datetime.now()
    form = WikiPageForm(user,course,modified_on,request.POST)
    
    if not form.is_valid():
        raise Http404

    content = form.cleaned_data['content']
    
    wikis = course.wiki.all()

    if len(wikis) == 1: #should be 1
        
        if content != wikis[0].content:
        	context['success'] = "Wiki <b> edited</b> successfully."
        else:# if the user does nothing.
        	context['course'] = course
    		context['content'] = content
        	return render(request, "pages/edit_wiki_page.html", context)

        wikis[0].content = content
        wikis[0].last_modified_on = form.modified_on
        wikis[0].user = form.user
        wikis[0].save()
        context['course'] = course
    	context['content'] = wikis[0].content

    
    else:
    	if len(wikis) == 0:
        	wiki = WikiPage.objects.create(last_modified_on=form.modified_on, content=content,last_modified_by=form.user,course=form.course)
        	context['success'] = "Wiki <b> created</b> successfully."
        	context['course'] = course
    		context['content'] = content
    	else: # this shouldn't happen (if we want to have only one wiki per course)
    		context['error'] = "Whoa ! Apparently there are more wikis for this course " 

	context['page'] = 'edit_wiki_page'
    return render(request, "pages/edit_wiki_page.html", context)

@login_required
def revert_wiki_page(request):
	pass

@login_required
def view_wiki_page(request,slug):
    context = {
        'page': 'view_wiki_page',
    }
    course = get_object_or_404(Course,slug=slug)
    wikis = course.wiki.all()
    if len(wikis) < 1:
        raise Http404
    else:
        wiki = wikis[0]
        context['content'] = wiki.content
        context['course'] = wiki.course

    return render(request,'pages/wiki/view_wiki.html',context)