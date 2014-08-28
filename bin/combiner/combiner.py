
import json

fall_courses = json.load( open('courseDetailsFall') )
spring_courses = json.load( open('courseDetailsSpring') )

for course in fall_courses:
    if 'Catalogue' in course:
        course['Catalogue'] = "Fall > " + course['Catalogue']
    else:
        print "Warning: No Catalogue!"

all_courses = fall_courses + spring_courses

all_courses_file = open('courseDetails', 'w')
all_courses_file.write( json.dumps(all_courses) )
all_courses_file.close()