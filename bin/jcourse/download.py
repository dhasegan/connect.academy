from app.models import *

reviews = []

comments = Comment.objects.all()
for comment in comments:
    context = {
        'course_name': comment.course.name,
        'course_id': comment.course.course_id,
        'datetime': str(comment.datetime),
        'review': comment.comment
    }
    details = CommentDetails.objects.get(comment=comment)
    if details.posted_by:
        context['posted_by'] = details.posted_by.username
    upvotes = details.upvoted_by.all()
    context['upvotes'] = []
    for upvote in upvotes:
        context['upvotes'].append( upvote.username )
    downvotes = details.downvoted_by.all()
    context['downvotes'] = []
    for downvote in downvotes:
        context['downvotes'].append( downvote.username )
    reviews.append( context )


ratings = []
old_ratings = Rating.objects.all()
for rating in old_ratings:
    context = {
        'course_name': rating.course.name,
        'course_id': rating.course.course_id,
        'posted_by': rating.user.username,
        'rating_type': rating.rating_type,
        'rating': rating.rating
    }
    if rating.rating_type == 'PRF':
        context['professor'] = rating.professor_rating.prof.name
    ratings.append(context)
