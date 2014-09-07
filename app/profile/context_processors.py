from django.conf import settings
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from app.context_processors import activity_context, paginated
from app.models import *

def profile_activities(request, user):
    activities_list = Activity.objects.filter(user=user).order_by('timestamp').reverse()
    activities_list = [x for x in activities_list if 
                                (not x.get_type() == "ForumPostActivity" 
                                 or not x.generalactivity.forumpostactivity.forum_post.anonymous)
                            and (not x.get_type() == "ForumAnswerActivity"
                                or not x.generalactivity.forumansweractivity.forum_answer.anonymous)
                            and (not x.get_type() == "ReviewActivity"
                                or not x.courseactivity.reviewactivity.review.anonymous)]

    activities_context = [activity_context(activity,user) for activity in activities_list]
    activities_context = sorted(activities_context,
                             key=lambda a: a['activity'].timestamp,
                             reverse=True) 
    return paginated(request,activities_context,20)



# loads NEW activities asynchronously, called with ajax
def new_profile_activities(request,user):
    last_id = long(request.GET.get('last_id'))
    
    activities_list = list(CourseActivity.objects.filter(user=user, id__gt=last_id).reverse())
    activities_list = [x for x in activities_list if 
                                (not hasattr(x,"forumpostactivity") 
                                 or not x.generalactivity.forumpostactivity.forum_post.anonymous)
                            and (not hasattr(x,"forumansweractivity")
                                or not x.generalactivity.forumansweractivity.forum_answer.anonymous)
                            and (not hasattr(x, "reviewactivity")
                                or not x.courseactivity.reviewactivity.review.anonymous)]
    
    activities_list = [a for a in activities_list if a.can_view(user)]

    activities_context = [activity_context(activity,user) for activity in activities_list]
    activities_context = sorted(activities_context,
                         key=lambda a: a['activity'].timestamp,
                         reverse=True)


    return activities_context 
