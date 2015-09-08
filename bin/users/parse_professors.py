import json

f = open('course_details-2015-Fall-01.json')
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

professorsFile = open('course_professors-2015-Fall-01.json', 'w')
professorsFile.write( json.dumps(professors) )
professorsFile.close()
