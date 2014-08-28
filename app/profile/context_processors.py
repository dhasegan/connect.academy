from django.conf import settings
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from app.context_processors import activity_context, paginated
from app.models import *

def profile_activities(request, user):
	activities_list = list(CourseActivity.objects.filter(user=user).reverse())
	activities_context = [activity_context(activity,user) for activity in activities_list]
	activities_context = sorted(activities_context,
                             key=lambda a: a['activity'].timestamp,
                             reverse=True)
	return paginated(request,activities_context, 20)



# loads NEW activities asynchronously, called with ajax
def new_profile_activities(request,user):
    last_id = long(request.GET.get('last_id'))
    
    activities_list = list(CourseActivity.objects.filter(user=user, id__gt=last_id).reverse())
    activities_context = [activity_context(activity,user) for activity in activities_list]
    activities_context = sorted(activities_context,
                         key=lambda a: a['activity'].timestamp,
                         reverse=True)

    return activities_context 
