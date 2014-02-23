from django.db import models

from django.contrib.auth.models import User
from django.utils.text import slugify
from django.conf import settings 
from app.course_info import *

class jUser(User):
    department = models.CharField(max_length=50)

class Professor(models.Model):
    name = models.CharField(max_length=50)
    department = models.CharField(max_length=50, blank=True, null=True)

    def __unicode__(self):
        return str(self.name)

class Rating(models.Model):
    user = models.ForeignKey('jUser')
    course = models.ForeignKey('Course')
    rating = models.FloatField()
    rating_type = models.CharField( max_length=3,
                                    choices=RATING_TYPES,
                                    default=OVERALL_R)

    def __unicode__(self):
        return str(self.rating)

class Professor_Rating(Rating):
    prof = models.ForeignKey('Professor')

    def __unicode__(self):
        return "Rating " + str(self.prof.name)

class Course(models.Model):
    course_id = models.CharField( max_length=10 )
    course_type = models.CharField( max_length=3,
                                    choices=COURSE_TYPES,
                                    default=LECTURE)
    name = models.CharField(max_length=200)
    instructors = models.ManyToManyField('Professor')
    credits = models.FloatField()
    description = models.CharField(max_length=5000, blank=True, null=True)
    additional_info = models.CharField(max_length=5000, blank=True, null=True)
    sections_info = models.CharField(max_length=5000, blank=True, null=True)
    catalogue = models.CharField(max_length=300)
    grades = models.CharField(max_length=1000, blank=True, null=True)
    grades_info = models.CharField(max_length=5000, blank=True, null=True)
    abbreviation = models.CharField(max_length=50, blank=True, null=True)
    participants = models.CharField(max_length=10, blank=True, null=True)
    hours_per_week = models.CharField(max_length=10, blank=True,null=True)

    slug = models.SlugField(max_length=200)
    image = models.ImageField(upload_to='courses')

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Course, self).save(*args, **kwargs)

    def __unicode__(self):
        return str(self.name)

class Comment(models.Model):
    course = models.ForeignKey('Course')
    comment = models.CharField(max_length=1000)
    datetime = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return "Comm" + str(self.id)
