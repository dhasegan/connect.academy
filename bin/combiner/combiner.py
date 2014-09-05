
import json

fall_courses = json.load( open('courseDetailsFall') )
spring_courses = json.load( open('courseDetailsSpring') )

all_courses = []
for course in fall_courses:
    if 'Catalogue' in course and 'Electrical Engineering and Computer Science' in course['Catalogue']:
        all_courses.append(course)
for course in spring_courses:
    if 'Catalogue' in course and 'Electrical Engineering and Computer Science' in course['Catalogue']:
        all_courses.append(course)

all_courses_file = open('courseDetails', 'w')
all_courses_file.write( json.dumps(all_courses) )
all_courses_file.close()