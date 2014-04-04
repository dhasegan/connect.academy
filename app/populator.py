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
        return (self.words[ random.randrange(len(self.words)) ]).encode("ascii", "ignore")

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
        fname = self.random_word().lower().replace("'", "")
        lname = self.random_word().lower().replace("'", "")
        username = fname + "-" + lname
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

    def populate_users(self, count):
        for i in range(count):
            self.add_user()

    def populate_database(self, universities, users):
        self.populate_universities(universities)
        self.populate_users(users)


