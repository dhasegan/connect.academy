
from django.utils import timezone
import pytz

# Insert results into the DB

from app.models import *
import json

f = open('bin/combiner/courseDetails')
coursesList = json.load(f)
f.close()

univ = University.objects.filter(name__contains="Jacobs")[0]
category = univ.get_university_category()

for courseDetails in coursesList:
    # print courseDetails['CourseName']
    if len(Course.objects.filter(name=courseDetails['CourseName'])) > 0:
        continue
    # Setup instructors
    dbProfs = []
    if 'Instructors' in courseDetails:
        instructors = courseDetails['Instructors'].split("; ")
        for instructor in instructors:
            last_name = instructor.split(' ')[-1]
            profs = jUser.objects.filter(last_name__contains=last_name)
            if len(profs) == 1:
                dbProfs.append(profs[0])
            elif len(profs) > 1:
                tents = []
                for p in profs:
                    ok = False
                    first_names = p.first_name.split(" ")
                    for fn in first_names:
                        if fn in instructor:
                            ok = True
                    if ok:
                        tents.append(p)
                if len(tents) == 0 or len(tents) > 1:
                    print "Couldnt find professor for course " + courseDetails['CourseName']
                else:
                    dbProfs.append(tents[0])
            else:
                print "Couldnt find professor for course " + courseDetails['CourseName']
    # Get Course type
    # ctype = False
    # for CTYPE in COURSE_TYPES:
    #     if 'Type' in courseDetails and CTYPE[1] == courseDetails['Type']:
    #         ctype = CTYPE[0]
    # if not ctype:
    #     print "Error! Didnt find course type " + courseDetails['CourseName'] + " in our models!"
    #     ctype = UNKNOWN
    # Get Credits number
    if 'Credits' in courseDetails:
        credits = float(courseDetails['Credits'][0:4])
    else:
        credits = 5.0
    # get category
    catalogue = courseDetails['Catalogue']
    categories = catalogue.split(" > ")
    current_category = category
    for cat in categories:
        children = current_category.children.filter(name=cat)
        if len(children):
            current_category = children[0]
        else:
            print "Error! Cannot find category for course " + courseDetails['CourseName']
    cid = 1
    if 'CourseID' in courseDetails and courseDetails['CourseID']:
        cid = int(courseDetails['CourseID'])
    # Create the Course class
    course = Course.objects.create(course_id = cid, name = courseDetails['CourseName'], credits = credits,
                    university=univ, category = current_category, external_link = courseDetails['CampunetLink'])
    if 'Official Course Description' in courseDetails:
        course.description = courseDetails['Official Course Description']
    if 'Course Name Abbreviation' in courseDetails and courseDetails['Course Name Abbreviation']:
        course.abbreviation = courseDetails['Course Name Abbreviation'],
    additional_info = ""
    additional_fields = ['Type', 'Hours per week', 'Min. | Max. participants', 'Partial Grades', 'Additional Information',\
        'This course is divided into the following sections', 'Further Grading Information']
    for field in additional_fields:
        if field in courseDetails and courseDetails[field]:
            additional_info += field + ": " + courseDetails[field] + "\n"
    if additional_info:
        course.additional_info = additional_info[0:5000]
    course.save()


    for dbProf in dbProfs:
        ProfessorCourseRegistration.objects.create(professor=dbProf, course=course, is_approved=True)

 