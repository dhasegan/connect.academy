import json

f = open('courseDetails')
coursesList = json.load(f)
f.close()

professors = []

for courseDetails in coursesList:
    print courseDetails['CourseName']
    if 'Instructors' in courseDetails:
        instructors = courseDetails['Instructors'].split("; ")
        for instructor in instructors:
            if instructor not in professors:
                professors.append(instructor)

professors = sorted(professors)

professorsFile = open('professors', 'w')
professorsFile.write( json.dumps(professors) )
professorsFile.close()