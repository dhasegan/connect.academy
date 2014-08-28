from app.models import *

import json

professors = json.load( open('bin/professors/professors_details.json') )

univ = University.objects.filter(name__contains="Jacobs")[0]

for username, details in professors.iteritems():
    user = jUser.objects.create_user(username=username, first_name=details['fname'], last_name=details['lname'],
        password="theotherside01", user_type=USER_TYPE_PROFESSOR, university=univ, is_confirmed=True)
    if "email" in details:
        user.email = details['email']
        user.is_active = True
    else:
        user.is_active = False
    description = ""
    if "title" in details and details['title']:
        description = description + "Title: " + details['title'] + "\n"
    if "deptinfo" in details and details['deptinfo']:
        description = description + "Department: " + details['deptinfo'] + "\n"
    if "phone" in details and details['phone']:
        description = description + "Phone: " + details['phone'] + "\n"
    if "room" in details and details['room']:
        description = description + "Room: " + details['room'] + "\n"
    if description:
        user.summary = description
    user.save()

