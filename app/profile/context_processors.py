from django.conf import settings
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from app.context_processors import activity_context, paginate_activities
from app.models import *


def profile_activities(request, user, logged_in_user):
    last_id = request.GET.get('last_id', None)
    ACTIVITIES_PER_PAGE = 20

    # Get the (unevaluated) profile page activities queryset
    activities_queryset = Activity.profile_page_activities(user)
    if last_id is not None:
        activities_queryset = activities_queryset.filter(id__lt=last_id)

    # Always get page 1, because we are filtering out activities with id >= last_id
    # (so we're only getting the older ones from the db)
    filtered_list = paginate_activities(activities_queryset, 1, ACTIVITIES_PER_PAGE, logged_in_user)


    activities_context = [activity_context(activity,user) for activity in filtered_list]
    return activities_context

# loads NEW activities asynchronously, called with ajax
def new_profile_activities(request, user, logged_in_user):
    last_id = long(request.GET.get('last_id', 0))
    
    # Provile activities 
    activities_list = Activity.profile_page_activities(user).filter(id__gt=last_id)
    activities_list = [a for a in activities_list if a.can_view(logged_in_user)]

    activities_context = [activity_context(activity,logged_in_user) for activity in activities_list]
    return activities_context  
