# Helpers
import random
import json

from app.models import *

class Populator:
    """ Class to populate the test database """
    def __init__(self):
        word_file = "/usr/share/dict/words"
        self.words = open(word_file).read().splitlines()

    def random_word(self):
        return random.choice(self.words).decode("utf-8", "ignore").replace("'", "")

    def add_university(self):
        while (True):
            name = self.random_word().capitalize() + " University"
            if len(University.objects.filter(name = name)) > 0:
                continue
            domain = name.lower().replace(" ", ".") + ".edu"
            University.objects.create(name=name, domain=domain)
            break

    def populate_universities(self, count):
        for i in range(count):
            self.add_university()

    def add_user(self):
        while True:
            fname = self.random_word().capitalize()
            lname = self.random_word().capitalize()
            username = fname[0] + "." + lname.lower()
            if len( jUser.objects.filter(username=username) ) > 0:
                continue
            univs = University.objects.all()
            univ = None
            if len(univs) == 0:
                add_university()
                univ = University.objects.all()[0]
            else:
                univ = univs[ random.randrange(len(univs)) ]
            active = True
            password = "1234"
            email = username + "@" + univ.domain
            user = jUser.objects.create_user(username=username, password=password,
                email=email, first_name=fname, last_name=lname)
            if random.random() < 0.05:
                user.is_active = False
                user.save()
            break

    def populate_users(self, count):
        for i in range(count):
            self.add_user()

    def add_professor(self):
        while True:
            name = self.random_word().capitalize() + self.random_word().capitalize()
            if len( Professor.objects.filter(name=name) ) > 0:
                continue
            department = self.random_word().capitalize() + " Science"
            prof = Professor(name=name, department=department)
            prof.save()
            break

    def populate_professors(self, count):
        for i in range(count):
            self.add_professor()

    def add_course(self):
        while True:
            course_id = random.randint(100000, 999999)
            if len(Course.objects.filter(course_id=course_id)) > 0:
                continue
            name = self.random_word() + " " + self.random_word() + " " + self.random_word()
            course_type = random.choice(list(COURSE_TYPES))[0]
            credits = random.randint(1,10)
            description = ""
            for i in range(0, random.randint(10,20)):
                description = description + self.random_word() + " "
            catalogue = ""
            for i in range(0, 3):
                description = description + self.random_word() + " > "

            # Add additional description
            # Add better catalogue
            # Add all other fields
            course = Course(course_id=course_id, course_type=course_type, name=name, 
                credits=credits, description=description, catalogue=catalogue)
            course.save()

            nr_instructors = random.randint(0,3)
            for i in range(nr_instructors):
                if len( Professor.objects.all() ) <= 3:
                    self.populate_professors(3)
                instructor = random.choice(Professor.objects.all())
                course.instructors.add(instructor)
            break

    def populate_courses(self, count):
        for i in range(count):
            self.add_course()

    def populate_database(self, nr_universities=3, nr_users=10, nr_professors=10, nr_courses=10):
        self.populate_universities(nr_universities)
        self.populate_users(nr_users)
        self.populate_professors(nr_professors)
        self.populate_courses(nr_courses)


