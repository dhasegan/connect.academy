# Helpers
import random
import json

# Project specific
from app.models import *
from django.utils import unittest
from app.populator import Populator


class PopulatorTest(unittest.TestCase):
    def test_empty_db(self):
        self.assertEqual( len(jUser.objects.all()), 0 )
        self.assertEqual( len(University.objects.all()), 0 )
        self.assertEqual( len(Professor.objects.all()), 0 )
        self.assertEqual( len(Rating.objects.all()), 0 )
        self.assertEqual( len(Professor_Rating.objects.all()), 0 )
        self.assertEqual( len(Course.objects.all()), 0 )
        self.assertEqual( len(Comment.objects.all()), 0 )

    def test_populate_db(self):
        populator = Populator()
        universities = 3
        users = 5
        populator.populate_database(universities=universities, users=users)
        self.assertEqual( len(University.objects.all()), universities)
        self.assertEqual( len(jUser.objects.all()), users)
