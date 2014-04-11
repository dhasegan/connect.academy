# Helpers
import random
import json
import sys

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

    def add_comment(self, course):
        comment = ""
        for i in range( random.randint(10, 30) ):
            comment = comment + self.random_word() + " "
        commObj = Comment(comment=comment, course=course)
        commObj.save()

    def populate_comments(self, count):
        courses = Course.objects.all()
        for i in range(count):
            course = random.choice( courses )
            self.add_comment(course)

    def add_rating(self, course):
        rating = ""
        users = list(jUser.objects.all())
        random.shuffle(users)
        rating_types = [] + list(RATING_TYPES)
        random.shuffle(rating_types)
        rater = None
        rat_type = None
        for rating_type in rating_types:
            for user in users:
                if len(Rating.objects.filter(user=user, course=course, rating_type=rating_type[0])) == 0:
                    rat_type = rating_type[0]
                    rater = user
                    break
        if rater == None:
            return False

        rating = random.randint(1,5)
        if rat_type != PROFESSOR_R:
            rat = Rating(user=rater, course=course, rating=rating, rating_type=rat_type)
            rat.save()
        else:
            prof = random.choice(course.instructors.all())
            rat = Professor_Rating(user=rater, course=course, rating=rating, rating_type=rat_type, prof=prof)
            rat.save()
        return True

    def populate_ratings(self, count):
        courses = Course.objects.all()
        for i in range(count):
            course = random.choice( courses )
            if len(Rating.objects.filter(course=course)) >= len(jUser.objects.all()) * len(RATING_TYPES):
                i -= 1
                continue
            while not self.add_rating(course):
                pass

    def check_dependencies(self, nr_universities=0, nr_users=0, \
        nr_professors=0, nr_courses=0, nr_comments=0, nr_ratings=0):
        if nr_universities + len(University.objects.all()) <= 0 \
            and (nr_users > 0 or nr_courses > 0):
            raise RuntimeError("Not enough universities in the DB")
        if nr_courses + len(Course.objects.all()) > 0 \
            and (nr_professors + len(Professor.objects.all()) <= 0):
            raise RuntimeError("Not enough professors in the DB")
        if nr_comments + len(Comment.objects.all()) > 0 \
            and (nr_courses + len(Course.objects.all()) <= 0):
            raise RuntimeError("Not enough courses in the DB")
        if nr_ratings + len(Rating.objects.all()) > (nr_courses + len(Course.objects.all())) * \
            (nr_users + len(jUser.objects.all())) * len(RATING_TYPES):
            raise RuntimeError("Not enough courses and/or users in the DB")

    def populate_database(self, nr_universities=0, nr_users=0, \
        nr_professors=0, nr_courses=0, nr_comments=0, nr_ratings=0):

        self.check_dependencies(nr_universities=nr_universities, nr_users=nr_users, 
            nr_professors=nr_professors, nr_courses=nr_courses, nr_comments=nr_comments,
            nr_ratings=nr_ratings)
        self.populate_universities(nr_universities)
        self.populate_users(nr_users)
        self.populate_professors(nr_professors)
        self.populate_courses(nr_courses)
        self.populate_comments(nr_comments)
        self.populate_ratings(nr_ratings)
