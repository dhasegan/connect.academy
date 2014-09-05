from app.models import *

import json

professors = json.load( open('bin/professors/professors_details.json') )
needed_professors = json.load( open('bin/professors/professors') )

univ = University.objects.filter(name__contains="Jacobs")[0]

used_profs = []

uname_to_prof = {}

for username, details in professors.iteritems():
    found = None
    for nprof in needed_professors:
        if details['lname'] in nprof:
            found = nprof
    if not found or found in used_profs:
        continue
    used_profs.append(found)
    index = len(used_profs)
    uname = "professor" + str(index)
    if jUser.objects.filter(username=uname).count() > 0:
        continue
    email = "professor" + str(index) + "@jacobs-university.de"
    user = jUser.objects.create(username=uname, first_name="Prof.", last_name="P" + str(index),
        password="1234", user_type=USER_TYPE_PROFESSOR, university=univ, is_confirmed=True, email=email)
    user.save()
    uname_to_prof["professor" + str(index)] = details


uname_file = open("bin/professors/uname_to_prof.json", "w")
uname_file.write( json.dumps(uname_to_prof) )
uname_file.close()

