import json
import urllib2
from urlparse import urlparse
from dateutil.parser import parse

from django.core.files import File
from django.core.files.temp import NamedTemporaryFile

from app.models import *

student_details = json.load(open('academy/jacobs_user_details.json'))
reviews = json.load( open('bin/jcourse/reviews.json') )
ratings = json.load( open('bin/jcourse/ratings.json') )
students = json.load( open('bin/jcourse/contr_users.json') )

univ = University.objects.filter(name__contains="Jacobs")[0]
category = univ.get_university_category()

# Populate students
for st in students:
    if st in student_details:
        if jUser.objects.filter(username=st).count() > 0:
            continue
        detail = student_details[st]
        user = jUser.objects.create_user(username=st, password="theotherside01",
            first_name=detail['first_name'], last_name=detail['last_name'], university=univ,
            email=detail['email'])
        user.is_active = True
        if 'description' in detail:
            user.summary = detail['description']
        if 'photourl' in detail:
            photo_url = detail['photourl']
            photo_ext = urlparse(photo_url).path.split('/')[-1].split('.')[-1]
            photo_name = st + "." + photo_ext
            img_temp = NamedTemporaryFile(delete=True)
            img_temp.write(urllib2.urlopen(photo_url).read())
            img_temp.flush()
            user.profile_picture.save(photo_name, File(img_temp), save=False)
        user.save()

jack = jUser.objects.get(username="jack")

not_found_reviews = []

# !!!!!!!!!!!!!! IMPORTANT BUG TO FIX!!!!!!!!!!!!!!!!!!1
# This populator creates 2 activity reviews for each review. Beware of the double poster
for review in reviews:
    cid = review['course_id'].replace("APS", "999")
    courses = Course.objects.filter(course_id=cid)
    if len(courses) != 1:
        courses = Course.objects.filter(name=review['course_name'])
        if len(courses) != 1:
            print "Cannot find for course " + review['course_name']
            not_found_reviews.append(review)
            continue
    course = courses[0]
    posted_by = jack
    if 'posted_by' in review and review['posted_by']:
        posters = jUser.objects.filter(username=review['posted_by'])
        if len(posters):
            posted_by = posters[0]
    anonymous = posted_by == jack
    r = Review.objects.create(course=course, posted_by=posted_by, anonymous=anonymous,
        review=review['review'])
    r.datetime = parse(review['datetime'])
    r.save()
    voters = []
    for up in review['upvotes']:
        upvoters = jUser.objects.filter(username=up)
        voter = jack
        if len(upvoters):
            voter = upvoters[0]
        if voter not in voters:
            voters.append(voter)
    for voter in voters:
        r.upvoted_by.add(voter)
    voters = []
    for up in review['downvotes']:
        downvoters = jUser.objects.filter(username=up)
        voter = jack
        if len(downvoters):
            voter = downvoters[0]
        if voter not in voters:
            voters.append(voter)
    for voter in voters:
        r.downvoted_by.add(voter)


unused_reviews_file = open('bin/jcourse/unused_reviews.json', 'w')
unused_reviews_file.write( json.dumps(not_found_reviews) )
unused_reviews_file.close()

not_found_ratings = []

for rating in ratings:
    cid = rating['course_id'].replace("APS", "999")
    courses = Course.objects.filter(course_id=cid)
    if len(courses) != 1:
        courses = Course.objects.filter(name=rating['course_name'])
        if len(courses) != 1:
            print "Cannot find for course " + rating['course_name']
            not_found_ratings.append(rating)
            continue
    course = courses[0]
    posted_by = jack
    if 'posted_by' in rating:
        posters = jUser.objects.filter(username=rating['posted_by'])
        if len(posters):
            posted_by = posters[0]
    r = Rating.objects.create(course=course, user=posted_by, rating=rating['rating'], rating_type=rating['rating_type'])
    if 'professor' in rating:
        prof_lname = rating['professor'].split(" ")[-1]
        professors = course.professors.filter(last_name__contains=prof_lname)
        if len(professors) == 1:
            pass
            r.professor = professors[0]
            r.save()
        else:
            print "Cannot find for professor " + rating['professor'] + \
                " in course " + rating['course_name']
            not_found_ratings.append(rating)
            continue

unused_ratings_file = open('bin/jcourse/unused_ratings.json', 'w')
unused_ratings_file.write( json.dumps(not_found_ratings) )
unused_ratings_file.close()
