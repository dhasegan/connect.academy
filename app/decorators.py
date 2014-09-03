from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse
from app.models import *

def require_student(view):
	def decorated(request, *args, **kwargs):
		if request.user is None or request.user.juser.user_type != USER_TYPE_ADMIN:
			raise Http404
		return view(request, *args, **kwargs)
	return decorated

def require_professor(view):
	def decorated(request, *args, **kwargs):
		if request.user is None or request.user.juser.user_type != USER_TYPE_PROFESSOR:
			raise Http404
		return view(request, *args, **kwargs)	
	return decorated

def require_admin(view):	
	def decorated(request, *args, **kwargs):
		if request.user is None or request.user.juser.user_type != USER_TYPE_ADMIN:
			raise Http404
		return view(request,*args, **kwargs)
	return decorated

# Active juser
def require_active_user(view):
	def decorated(request, *args, **kwargs):
		if not request.user:
			raise Http404
		juser = get_object_or_404(jUser, id=request.user.id)
		if not juser.is_active:
			return HttpResponseRedirect(reverse('error_page', args=["not-active"]))
		return view(request,*args, **kwargs)
	return decorated


# This decorator takes a list of USER_TYPE ints and raises Http404 if the logged in user
# is not of any type mentioned in the list 
# example usage:

# @require_user_type([USER_TYPE_PROFESSOR, USER_TYPE_ADMIN])
# def view(request):
# 	#view body
def require_user_type(type_list):
	def check_type(view):
		def decorated(request, *args, **kwargs):
			user = request.user.juser
			if user is None or not user.user_type in type_list:
				raise Http404
			return view(request, *args, **kwargs)
		return decorated
	return check_type
