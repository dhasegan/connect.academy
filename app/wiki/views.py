from mimetypes import guess_type
import hashlib
import string
import random
import datetime
import pytz

from django.core.context_processors import csrf
from django.shortcuts import render, redirect, get_object_or_404, render_to_response
from django.http import Http404, HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.tokens import default_token_generator
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.views.decorators.http import require_GET, require_POST
from django.db import transaction
import reversion

from app.models import *
from app.context_processors import *
from app.wiki.forms import *
from app.wiki.helpers import *

#TODO only users registered for the course should open this page.
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
    	#also add the revision history here
    return render(request,"pages/edit_wiki_page.html",context)


@transaction.atomic()
@reversion.create_revision()
@login_required
def save_wiki_page(request,slug):
    context = {
        "page":"save_wiki_page"
    }
    context.update(csrf(request))
    course = Course.objects.get(slug=slug)
    if request.POST:
        user = request.user
        modified_on = datetime.now(pytz.UTC)
        form = WikiPageForm(course,modified_on,request.POST)
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
        else:# if the user does nothing.
        	context['title'] = title
    		context['content'] = content
        	return render(request, "pages/edit_wiki_page.html", context)

        wikis[0].title = title
        wikis[0].content = content
        edited_on = datetime.now(pytz.UTC)
        ContributedToWiki.objects.create(wiki=wikis[0],user=request.user,modified_on=datetime.now(pytz.UTC))
        
        wikis[0].save()
        context['title'] = wikis[0].title
    	context['content'] = wikis[0].content
    else:
    	if len(wikis) == 0:
        	wiki = WikiPage.objects.create(title=title, content=content,course=form.course)
        	edited_on = datetime.now(pytz.UTC)
        	ContributedToWiki.objects.create(wiki=wiki,user=request.user,modified_on=edited_on)	
        	
        	context['success'] = "Wiki <b> created</b> successfully."
        	context['title'] = title
    		context['content'] = content
    	else: # this shouldn't happen (if we want to have only one wiki per course)
    		context['error'] = "Whoa ! Apparently there are more wikis for this course " 

	
    return render(request, "pages/edit_wiki_page.html", context)

@login_required
def revert_wiki_page(request,slug):
	context = {
		"page":"revert_wiki_page"
	}
	course = Course.objects.get(slug=slug)
	wikis = course.wiki.all()
	context['course'] = course
	context = dict(context.items() + course_page_context(request, course).items())

	if len(wikis) == 1:
		wiki = wikis[0]
		version_list = reversion.get_unique_for_object(wiki)
		if len(version_list) <= 1: # only the current version is stored in the version table.
			context['error'] = "No revisions for this wiki. Cannot revert."
			context['title'] = wiki.title
			context['content'] = wiki.content
			return render(request,"pages/course.html",context)
		else:
			#there multiple revisions.
			#for some reason 'previous_version.revision.revert(delete=True)' which should revert to the previous version and deleting the ones after that doesn't work.
			#Using a ugly hack for that. 
			
			current_version_index = find_position_in_version_list(version_list,wiki)
			
			if current_version_index == -1: # error, shouldn't happen though.
				context['error'] = "Oops, something went wrong while <b>reverting</b>."
				return render(request,"pages/course.html",context)
			if current_version_index == len(version_list) - 1 : # no previous positions
				context['error'] = "No older versions for this wiki. Cannot revert."
				return render(request,"pages/course.html",context)
			
			ret_val = revert_previous_version(version_list,version_list[current_version_index])
			if not ret_val:
				context['error'] = "Oops, something went wrong while <b>reverting</b>."
				return render(request,"pages/course.html",context)	

			context['success'] = "Successfully reverted the wiki."
	
	return render(request,"pages/course.html",context)
