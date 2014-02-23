from app.models import *
from django.utils.dateformat import format

comments = Comment.objects.all()
commdict = []
for c in comments:
  d = {
    'course_id': c.course.course_id,
    'course_name': c.course.name,
    'comment': c.comment,
    'datetime': format(c.datetime, 'U')
  }
  commdict.append( d )

import json
import sys
json.dumps(commdict, sys.stdout)