# Helpers
import random
import json

# Project specific
from app.models import *
from app.populator import Populator

# Test specifics
from django.utils import unittest
from django.test import TestCase
from django.test.client import Client

class WelcomePageTest(TestCase):
    """
    @title WelcomePageTest
    @description Tests the '/welcome' and '/' urls with the associate view
    """

    def setUp(self):
        self.client = Client()

    def test_entry_pages(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        response = self.client.get('/welcome')
        self.assertEqual(response.status_code, 200)

        response = self.client.post('/')
        self.assertEqual(response.status_code, 200)
        response = self.client.post('/welcome')
        self.assertEqual(response.status_code, 200)

class LoginActionTest(TestCase):
    """
    @title LoginActionTest
    @description Tests the '/login' url with the associate view
    """

    def setUp(self):
        Populator().populate_database(nr_universities=3, nr_users=5)
        self.client = Client(enforce_csrf_checks=False)

    def test_entry_pages(self):
        response = self.client.get('/login')
        self.assertEqual(response.status_code, 404)
        response = self.client.post('/login')
        self.assertEqual(response.status_code, 404)

    def test_logging(self):
        users = jUser.objects.all()
        self.assertFalse(len(users) == 0)
        user = random.choice(users)
        response = self.client.post('/login', {
            'username': user.username,
            'password': '1234'
        })
        # The Django test framework cannot authenticate the user of the request
        # But it will return a redirect 302
        self.assertEqual(response.status_code, 302)

    def test_fake_logging(self):
        # Bad username
        response = self.client.post('/login', {
            'username': '000000',
            'password': '1234'
        })
        self.assertEqual(response.status_code, 200)
        # Bad password
        users = jUser.objects.all()
        self.assertFalse(len(users) == 0)
        user = random.choice(users)
        response = self.client.post('/login', {
            'username': user.username,
            'password': '4321'
        })
        self.assertEqual(response.status_code, 200)

    def test_bad_request(self):
        # Bad username name
        users = jUser.objects.all()
        self.assertFalse(len(users) == 0)
        user = random.choice(users)
        response = self.client.post('/login', {
            'usrname': user.username,
            'password': '1234'
        })
        self.assertEqual(response.status_code, 404)
        # Bad password name
        response = self.client.post('/login', {
            'username': user.username,
            'paswd': '1234'
        })
        self.assertEqual(response.status_code, 404)
        # Bad request type
        response = self.client.get('/login', {
            'username': user.username,
            'password': '1234'
        })
        self.assertEqual(response.status_code, 404)
        # Bad both username and password
        response = self.client.get('/login', {
            'usr': user.username,
            'pwsd': '1234'
        })
        self.assertEqual(response.status_code, 404)


class HomePageTest(TestCase):
    def setUp(self):
        self.nr_courses = 10
        Populator().populate_database(nr_universities=3, nr_users=5, \
            nr_professors=self.nr_courses, nr_courses=self.nr_courses, nr_ratings=100)
        self.client = Client()
        user = random.choice( jUser.objects.all() )
        self.client.login(username=user.username, password='1234')

    def test_entry_pages(self):
        response = self.client.get('/home')
        self.assertEqual(response.status_code, 200)

    def test_proper_context(self):
        response = self.client.get('/home')
        self.assertTrue("page" in response.context and response.context["page"] != "")
        self.assertEquals(response.context["page"], "home")
        self.assertTrue("courses" in  response.context)
        self.assertEquals( len(response.context["courses"]), self.nr_courses )
        courses = response.context["courses"]
        for course in courses:
            profs = list(course["course"].instructors.all())
            self.assertEquals(len(profs), len(course["profs"]))
            for i in range(len(profs)):
                self.assertEqual(profs[i].name, course["profs"][i].name)

    def test_sorted_by_rating(self):
        response = self.client.get('/home')
        self.assertTrue("courses" in  response.context)
        self.assertEquals( len(response.context["courses"]), self.nr_courses )
        courses = response.context["courses"]
        for i in range(len(courses)-1):
            self.assertTrue( courses[i]['overall_rating'] >= courses[i+1]['overall_rating'] )

class CoursePageTest(TestCase):
    def setUp(self):
        self.nr_users = 5
        self.nr_courses = 4
        self.nr_ratings = 16
        Populator().populate_database(nr_universities=3, nr_users=self.nr_users, \
            nr_professors=10, nr_courses=self.nr_courses, nr_comments=20, nr_ratings=self.nr_ratings)
        self.client = Client()
        user = random.choice( jUser.objects.all() )
        self.client.login(username=user.username, password='1234')

    def test_entry_pages(self):
        courses = Course.objects.all()
        for course in courses:
            response = self.client.get('/course/' + course.slug)
            self.assertEqual(response.status_code, 200)

    def test_proper_context(self):
        courses = Course.objects.all()
        for course in courses:
            response = self.client.get('/course/' + course.slug)
            self.assertTrue("page" in response.context and response.context["page"] != "")
            self.assertEquals(response.context["page"], "course")
            self.assertTrue("course" in response.context)
            self.assertEquals( course, response.context['course'] )

            self.assertTrue("instructors" in response.context)
            profs = list(course.instructors.all())
            self.assertEquals(len(profs), len(response.context["instructors"]))
            for i in range(len(profs)):
                self.assertEqual(profs[i].name, response.context["instructors"][i].name)

            self.assertTrue("comments" in response.context)
            comments = Comment.objects.filter(course=course)
            self.assertEquals(len(comments), len(response.context["comments"]))

class AllCommentsPageTest(TestCase):
    def setUp(self):
        self.nr_comments = 50
        Populator().populate_database(nr_universities=3, nr_users=5, \
            nr_professors=10, nr_courses=10, nr_comments=self.nr_comments)
        self.client = Client()
        user = random.choice( jUser.objects.all() )
        self.client.login(username=user.username, password='1234')

    def test_entry_pages(self):
        response = self.client.get('/all_comments')
        self.assertEqual(response.status_code, 200)

    def test_proper_context(self):
        response = self.client.get('/all_comments')
        self.assertTrue("page" in response.context and response.context["page"] != "")
        self.assertEquals(response.context["page"], "all_comments")
        self.assertTrue("comments" in response.context)
        self.assertEquals( len(response.context["comments"]), self.nr_comments)

class PopulatorTest(TestCase):
    def test_empty_db(self):
        self.assertEqual( len(jUser.objects.all()), 0 )
        self.assertEqual( len(University.objects.all()), 0 )
        self.assertEqual( len(Professor.objects.all()), 0 )
        self.assertEqual( len(Rating.objects.all()), 0 )
        self.assertEqual( len(Professor_Rating.objects.all()), 0 )
        self.assertEqual( len(Course.objects.all()), 0 )
        self.assertEqual( len(Comment.objects.all()), 0 )
        self.assertEqual( len(Rating.objects.all()), 0 )

    def test_populate_db(self):
        populator = Populator()
        nr_universities = 3
        nr_users = 5
        nr_professors = 10
        nr_courses = 10
        nr_comments = 30
        nr_ratings = 30
        populator.populate_database(nr_universities=nr_universities, nr_users=nr_users,
            nr_professors=nr_professors, nr_courses=nr_courses, nr_comments=nr_comments,
            nr_ratings=nr_ratings)
        self.assertEqual( len(University.objects.all()), nr_universities)
        self.assertEqual( len(jUser.objects.all()), nr_users)
        self.assertEqual( len(Professor.objects.all()), nr_professors)
        self.assertEqual( len(Course.objects.all()), nr_courses)
        self.assertEqual( len(Comment.objects.all()), nr_comments)
        self.assertEqual( len(Rating.objects.all()), nr_ratings)
