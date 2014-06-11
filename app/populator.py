import random

from app.models import *


class JacobsPopulator:

    """ Class to populate the test database with Jacobs needed data """

    def __init__(self):
        pass

    @staticmethod
    def populate():
        uni = University(name="Jacobs University Bremen")
        uni.save()
        dom = Domain(name="jacobs-university.de", university=uni)
        dom.save()


class Populator:

    """ Class to populate the test database """

    def __init__(self):
        word_file = "/usr/share/dict/words"
        self.words = open(word_file).read().splitlines()

    def random_word(self):
        while True:
            try:
                word = random.choice(self.words).decode("utf-8", "ignore").replace("'", "")
                if len(word) > 2:
                    return word
            except UnicodeError:
                continue

    def add_university(self):
        while (True):
            name = self.random_word().capitalize() + " University"
            if len(University.objects.filter(name=name)) > 0:
                continue
            univ = University.objects.create(name=name)

            domain = name.lower().replace(" ", ".") + ".edu"
            Domain.objects.create(name=domain, university=univ)
            break

    def populate_universities(self, count):
        for i in range(count):
            self.add_university()

    def add_juser(self, user_type=None):
        while True:
            fname = self.random_word().capitalize()
            lname = self.random_word().capitalize()
            username = fname[0] + "." + lname.lower()
            if len(jUser.objects.filter(username=username)) > 0:
                continue
            univs = University.objects.all()
            univ = univs[random.randrange(len(univs))]
            active = True
            password = "1234"
            domain = univ.domains.all()[0]
            email = username + "@" + domain.name
            if user_type == None:
                user_type = random.choice( list(USER_TYPES) )[0]
            user = jUser.objects.create_user(username=username, password=password,
                                             email=email, first_name=fname, last_name=lname,
                                             user_type=user_type)
            break

    def populate_jusers(self, count):
        for i in range(count):
            self.add_juser()

    def populate_students(self, count):
        for i in range(count):
            self.add_juser(USER_TYPE_STUDENT)

    def populate_admins(self, count):
        for i in range(count):
            self.add_juser(USER_TYPE_ADMIN)

    def populate_professors(self, count):
        for i in range(count):
            self.add_juser(USER_TYPE_PROFESSOR)

    def add_category(self):
        while True:
            categories = Category.objects.all()
            parent = None
            level = 0
            name = "Connect.Academy"
            abbreviation = "connect"
            if len(categories):
                parent = random.choice(categories)
                level = parent.level + 1
                fname = self.random_word().capitalize()
                lname = self.random_word().capitalize()
                name = fname + " " + lname
                abbreviation = fname[0:min(len(fname),4)] + lname[0:min(len(lname),4)]
            category = Category(parent=parent, name=name, level=level, abbreviation=abbreviation)
            category.save()
            break

    def populate_categories(self, count):
        for i in range(count):
            self.add_category()

    def add_course(self, leaf_categories=None):
        if not leaf_categories:
            categories = Category.objects.all()
            leaf_categories = []
            for category in categories:
                is_leaf = True
                for checking_category in categories:
                    if checking_category.parent == category:
                        is_leaf = False
                if is_leaf:
                    leaf_categories.append( category )

        while True:
            course_id = random.randint(100000, 999999)
            name = self.random_word() + " " + self.random_word() + " " + self.random_word()
            course_type = random.choice(list(COURSE_TYPES))[0]
            credits = random.randint(1, 10)
            description = ""
            for i in range(0, random.randint(10, 20)):
                description = description + self.random_word() + " "
            category = random.choice( leaf_categories )
            universities = University.objects.all()
            if not universities:
                self.add_university()
            universities = University.objects.all()
            university = random.choice(universities)

            # Add additional description
            # Add all other fields
            course = Course(course_id=course_id, course_type=course_type, name=name,
                            credits=credits, description=description, category=category,
                            university=university)
            course.save()

            professors = list(jUser.objects.filter(user_type=USER_TYPE_PROFESSOR))
            if not professors:
                self.populate_professors(1)
            random.shuffle(professors)
            nr_professors = random.randint(1, 3)
            for i in range(nr_professors):
                pcr = ProfessorCourseRegistration(professor=professors[i], course=course)
                pcr.save()
            break

    def populate_courses(self, count):
        categories = Category.objects.all()
        leaf_categories = []
        for category in categories:
            is_leaf = True
            for checking_category in categories:
                if checking_category.parent == category:
                    is_leaf = False
            if is_leaf:
                leaf_categories.append( category )

        for i in range(count):
            self.add_course(leaf_categories)

    def add_comment(self, course):
        comment = ""
        for i in range(random.randint(10, 100)):
            comment = comment + self.random_word() + " "
        commObj = Review(comment=comment, course=course)
        commObj.save()

    def populate_comments(self, count):
        courses = Course.objects.all()
        for i in range(count):
            course = random.choice(courses)
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
            if rater:
                break
        if not rater:
            return False

        rating = random.randint(1, 5)
        if rat_type != PROFESSOR_R:
            rat = Rating(user=rater, course=course, rating=rating, rating_type=rat_type)
            rat.save()
        else:
            prof = random.choice(course.professors.all())
            rat = Rating(user=rater, course=course, rating=rating, rating_type=rat_type, professor=prof)
            rat.save()
        return True

    def populate_ratings(self, count):
        courses = Course.objects.all()
        for i in range(count):
            course = random.choice(courses)
            if len(Rating.objects.filter(course=course)) >= len(jUser.objects.all()) * len(RATING_TYPES):
                i -= 1
                continue
            while not self.add_rating(course):
                pass

    def check_dependencies(self, nr_universities=0, nr_students=0, nr_categories=0,
                           nr_professors=0, nr_courses=0, nr_reviews=0, nr_ratings=0):
        if nr_universities + len(University.objects.all()) <= 0 \
            and (nr_students > 0 or nr_courses > 0):
            raise RuntimeError("Not enough universities in the DB")
        if nr_courses > 0 and nr_categories + len(Category.objects.all()) < 2:
            raise RuntimeError("Not enough categories in the DB")
        if nr_courses + len(Course.objects.all()) > 0 \
            and (nr_professors + len(jUser.objects.filter(user_type=USER_TYPE_PROFESSOR)) <= 0):
            raise RuntimeError("Not enough professors in the DB")
        if nr_reviews + len(Review.objects.all()) > 0 \
            and (nr_courses + len(Course.objects.all()) <= 0):
            raise RuntimeError("Not enough courses in the DB")
        if nr_ratings + len(Rating.objects.all()) > (nr_courses + len(Course.objects.all())) * \
            (nr_students + len(jUser.objects.all())) * len(RATING_TYPES):
            raise RuntimeError("Not enough courses and/or users in the DB")

    def populate_database(self, nr_universities=0, nr_students=0, nr_categories=0,
                          nr_professors=0, nr_courses=0, nr_reviews=0, nr_ratings=0):

        self.check_dependencies(nr_universities=nr_universities, nr_students=nr_students, nr_categories=nr_categories,
                                nr_professors=nr_professors, nr_courses=nr_courses, nr_reviews=nr_reviews,
                                nr_ratings=nr_ratings)
        self.populate_universities(nr_universities)
        self.populate_students(nr_students)
        self.populate_professors(nr_professors)
        self.populate_categories(nr_categories)
        self.populate_courses(nr_courses)
        self.populate_comments(nr_reviews)
        self.populate_ratings(nr_ratings)
