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
    }
    course = Course.objects.get(slug=slug)
    wikis = course.wiki.all()
    if len(wikis) > 0:
    	wiki = wikis[0]
    	context['title'] = wiki.title
       	context['content'] = wiki.content
    	
    else:
    	context['title'] = course.name
        context['content'] = ""
    	
    return render(request,"pages/edit_wiki_page.html",context)

    

#@transaction.atomic()
#@reversion.create_revision()
@login_required
def save_wiki_page(request,slug):
    context = {
        "page":"save_wiki_page"
    }
    context.update(csrf(request))
    course = Course.objects.get(slug=slug)
    if request.POST:
        user = request.user
        modified_on = datetime.now()
        form = WikiPageForm(user,course,modified_on,request.POST)
    else:
    	raise Http404
    
    if not form.is_valid():
        raise Http404

    title = form.cleaned_data['title']
    content = form.cleaned_data['content']
    
    wikis = course.wiki.all()

    if len(wikis) == 1: #should be 1
        
        if title != wikis[0].title or content != wikis[0].content:
        	context['success'] = "Wiki <b> edited</b> successfully."
        else:
        	pass
        wikis[0].title = title
        wikis[0].content = content
        wikis[0].last_modified_on = form.modified_on
        wikis[0].user = form.user
        wikis[0].save()
        context['title'] = wikis[0].title
    	context['content'] = wikis[0].content

    
    else:
    	if len(wikis) == 0:
        	wiki = WikiPage.objects.create(last_modified_on=form.modified_on, title=title, content=content,last_modified_by=form.user,course=form.course)
        	context['success'] = "Wiki <b> created</b> successfully."
        	context['title'] = title
    		context['content'] = content
    	else: # this shouldn't happen (if we want to have only one wiki per course)
    		context['error'] = "Whoa ! Apparently there are more wikis for this course " 

	
    return render(request, "pages/edit_wiki_page.html", context)

@login_required
def revert_wiki_page(self,request):
	pass