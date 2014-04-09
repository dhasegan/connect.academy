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
        Populator().populate_database(nr_universities=3, nr_users=5, nr_courses=self.nr_courses)
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

class AllCommentsPageTest(TestCase):
    def setUp(self):
        self.nr_comments = 50
        Populator().populate_database(nr_universities=3, nr_users=5, nr_comments=self.nr_comments)
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

    def test_populate_db(self):
        populator = Populator()
        universities = 3
        users = 5
        populator.populate_database(nr_universities=universities, nr_users=users)
        self.assertEqual( len(University.objects.all()), universities)
        self.assertEqual( len(jUser.objects.all()), users)
