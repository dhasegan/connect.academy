import json
import os

professors = json.load( open('professors.json') )

for prof in professors:
    last_name = prof.split(" ")[-1]
    os.system("python get_users.py " + last_name)
