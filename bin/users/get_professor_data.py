import json
import os

professors = json.load( open('course_professors-2015-Fall-01.json') )

for prof in professors:
    last_name = prof.split(" ")[-1]
    print str(last_name.encode('utf-8'))
    os.system("python get_users.py " + last_name)
