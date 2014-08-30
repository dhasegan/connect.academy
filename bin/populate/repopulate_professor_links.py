
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
    if len(Course.objects.filter(name=courseDetails['CourseName'])) == 0:
        continue
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
        course = Course.objects.filter(name=courseDetails['CourseName'])[0]
        already_professors = course.professors.all()
        for dbProf in dbProfs:
            if dbProf not in already_professors:
                pcr = ProfessorCourseRegistration.objects.create(professor=dbProf, course=course, is_approved=True)

