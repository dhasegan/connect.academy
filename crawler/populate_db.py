
# Insert results into the DB

from app.models import *
from json import loads

f = open('crawler/courseDetails')
courseDetailsString = f.readline()
f.close()

coursesList = loads(courseDetailsString)

for courseDetails in coursesList:
    print courseDetails['CourseName']
    if len(Course.objects.filter(name=courseDetails['CourseName'])) > 0:
        continue
    # Setup instructors
    dbProfs = []
    instructors = courseDetails['Instructors'].split("; ")
    for instructor in instructors:
        prof = False
        profs = Professor.objects.filter(name=instructor)
        if len(profs) > 0:
            prof = profs[0]
        else:
            prof = Professor(name=unicode(instructor))
            prof.save()
        if prof:
            dbProfs.append(prof)
    # Get Course type
    ctype = False
    for CTYPE in COURSE_TYPES:
        if 'Type' in courseDetails and CTYPE[1] == courseDetails['Type']:
            ctype = CTYPE[0]
    if not ctype:
        print "Error! Didnt find course type " + courseDetails['CourseName'] + " in our models!"
        ctype = UNKNOWN
    # Get Credits number
    if 'Credits' in courseDetails:
        credits = float(courseDetails['Credits'][0:4])
    else:
        credits = 5.0
    # Create the Course class
    course = Course(course_id = courseDetails['CourseID'],
                    course_type = ctype,
                    name = courseDetails['CourseName'],
                    credits = credits,
                    catalogue = courseDetails['Catalogue'],
                    abbreviation = courseDetails['Course Name Abbreviation'])
    if 'Official Course Description' in courseDetails:
        course.description = courseDetails['Official Course Description']
    if 'Min. | Max. participants' in courseDetails and courseDetails['Min. | Max. participants'] != '- | -':
        course.participants = courseDetails['Min. | Max. participants']
    if 'Hours per week' in courseDetails:
        course.hours_per_week = courseDetails['Hours per week']
    if 'Partial Grades' in courseDetails and courseDetails['Partial Grades'] != "":
        course.grades = courseDetails['Partial Grades']
    if 'Additional Information' in courseDetails:
        course.additional_info = courseDetails['Additional Information']
    if 'This course is divided into the following sections' in courseDetails:
        course.sections_info = courseDetails['This course is divided into the following sections']
    if 'Further Grading Information' in courseDetails:
        course.grades_info = courseDetails['Further Grading Information']
    course.save()
    for dbProf in dbProfs:
        course.instructors.add(dbProf)

