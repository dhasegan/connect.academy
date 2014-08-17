from django.conf import settings
from django.contrib import admin

from .models import *

# !Respect the privacy of our users!
class RatingAdmin(admin.ModelAdmin):
    exclude = ('user',)
admin.site.register(Rating, RatingAdmin)

class ReviewAdmin(admin.ModelAdmin):
    exclude = ('posted_by', 'upvoted_by', 'downvoted_by',)
admin.site.register(Review, ReviewAdmin)

class ForumPostAdmin(admin.ModelAdmin):
    exclude = ('posted_by', 'upvoted_by', 'downvoted_by',)
admin.site.register(ForumPost, ForumPostAdmin)

class ForumAnswerAdmin(admin.ModelAdmin):
    exclude = ('posted_by', 'upvoted_by', 'downvoted_by',)
admin.site.register(ForumAnswer, ForumAnswerAdmin)

class CourseHomeworkSubmissionAdmin(admin.ModelAdmin):
    exclude = ('document', 'submitter', 'name',)
admin.site.register(CourseHomeworkSubmission)

# Everything public
admin.site.register(jUser)
admin.site.register(StudentCourseRegistration)
admin.site.register(ProfessorCourseRegistration)
admin.site.register(Major)
admin.site.register(Course)
admin.site.register(CourseTopic)
admin.site.register(Tag)
admin.site.register(University)
admin.site.register(Category)
admin.site.register(Domain)
admin.site.register(Deadline)
admin.site.register(CourseRegistrationDeadline)
admin.site.register(CourseDocument)
admin.site.register(CourseHomeworkRequest)
admin.site.register(Forum)
admin.site.register(ForumTag)
admin.site.register(ForumTopicTag)
admin.site.register(ForumExtraTag)
admin.site.register(WikiContributions)
admin.site.register(WikiPage)
