import json
import os

professors = json.load( open('professors.json') )

all_results = {}
not_found = []
for prof in professors:
    last_name = prof.split(" ")[-1].encode('utf-8')
    file_name = last_name + ".json"
    if os.path.exists(file_name)
        prof_file = open(file_name)
        results = json.load( prof_file )
        if len(results) == 1:
            
        elif len(results) == 0:
            not_found.append( prof )
        else:
    else:
        not_found.append( prof )

not_found_file = open('not_found.json')
not_found_file.write( json.dumps(not_found) )
not_found_file.close()
