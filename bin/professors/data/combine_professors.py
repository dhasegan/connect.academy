import json
import os

professors = json.load( open('professors.json') )

all_results = {}
not_found = []
for prof in professors:
    last_name = prof.split(" ")[-1].encode('utf-8')
    file_name = last_name + ".json"
    if os.path.exists(file_name):
        prof_file = open(file_name)
        results = json.load( prof_file )
        if len(results) == 1:
            details = results[0]
            all_results[ details['account'] ] = details
        elif len(results) == 0:
            not_found.append( prof )
        else:
            name_parts = prof.split(" ")
            found = []
            for result in results:
                ok = False
                if last_name == result['lname']:
                    for part in name_parts:
                        if part != last_name and part in result['fname']:
                            ok = True
                if ok:
                    found.append(result)
            if not found:
                all_results[ prof ] = results
            else:
                if len(found) == 1:
                    all_results[ found[0]['account'] ] = found[0]
                else:
                    all_results[ prof ] = found
    else:
        not_found.append( prof )

not_found_file = open('not_found.json', 'w')
not_found_file.write( json.dumps(not_found) )
not_found_file.close()

all_results_file = open('all_results.json', 'w')
all_results_file.write( json.dumps(all_results) )
all_results_file.close()