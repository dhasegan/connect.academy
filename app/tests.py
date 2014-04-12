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

class SubmitCommentTest(TestCase):
    def setUp(self):
        self.nr_comments = 5
        Populator().populate_database(nr_universities=3, nr_users=5, \
            nr_professors=10, nr_courses=10, nr_comments=self.nr_comments)
        self.client = Client()
        user = random.choice( jUser.objects.all() )
        self.client.login(username=user.username, password='1234')

    def test_entry_pages(self):
        response = self.client.get('/submit_comment')
        self.assertEqual(response.status_code, 404)
        response = self.client.post('/submit_comment')
        self.assertEqual(response.status_code, 404)

    def test_posting_comment(self):
        course = random.choice( Course.objects.all() )
        comment_text = "Comment text to be inserted"
        response = self.client.post('/submit_comment', {
            "course_id": course.id,
            "comment": comment_text,
            "url": "/course/" + course.slug, # Should be removed after refactoring
            })
        self.assertEqual(response.status_code, 302)

        comm = Comment.objects.filter( comment=comment_text )
        self.assertEquals( len(comm), 1 )
        self.assertEquals(comm[0].course, course)
        comms = Comment.objects.all()
        self.assertEquals( len(comms), self.nr_comments + 1 )

    def test_bad_request(self):
        course = random.choice( Course.objects.all() )
        comment_text = "Comment text to be inserted"

        response = self.client.post('/submit_comment', {
            "comment": comment_text,
            "url": "/course/" + course.slug,
            })
        self.assertEqual(response.status_code, 404)

        response = self.client.post('/submit_comment', {
            "course_id": course.id,
            "url": "/course/" + course.slug,
            })
        self.assertEqual(response.status_code, 404)

        response = self.client.post('/submit_comment', {
            "course_id": course.id,
            "comment": "",
            "url": "/course/" + course.slug,
            })
        self.assertEqual(response.status_code, 404)

        # TODO: If the number of characters is too high

class RateCourseTest(TestCase):
    def setUp(self):
        self.nr_ratings = 5
        Populator().populate_database(nr_universities=3, nr_users=5, \
            nr_professors=10, nr_courses=10, nr_comments=2, nr_ratings=self.nr_ratings)
        self.client = Client()

        Populator().populate_database(nr_users=1)
        users = jUser.objects.all()
        self.user = users[ len(users) - 1 ]
        self.client.login(username=self.user.username, password='1234')

    def test_entry_pages(self):
        response = self.client.get('/rate_course')
        self.assertEqual(response.status_code, 404)
        response = self.client.post('/rate_course')
        self.assertEqual(response.status_code, 404)

    def test_rating_course(self):
        for rating_type in RATING_TYPES:
            course = random.choice( Course.objects.all() )
            rating = random.randint(1,5)
            post_context = {
                "course_id": course.id,
                "rating_value": rating,
                "rating_type": rating_type[0],
                "url": "/course/" + course.slug, # Should be removed after refactoring
                }
            if rating_type[0] == PROFESSOR_R:
                post_context['profname'] = random.choice(course.instructors.all()).name
            response = self.client.post('/rate_course', post_context)
            self.assertEqual(response.status_code, 302)

            self.assertEquals( len(Rating.objects.all()), self.nr_ratings + 1 )
            self.nr_ratings += 1
            rat = Rating.objects.filter( user=self.user, rating_type=rating_type[0] )
            self.assertEquals( len(rat), 1 )
            self.assertEquals(rat[0].course, course)
            self.assertEquals(rat[0].rating, rating)

        ratings = Rating.objects.filter( user=self.user )
        self.assertEquals(len(ratings), len(RATING_TYPES))

    def test_bad_request(self):
        for rating_type in RATING_TYPES:
            course = random.choice( Course.objects.all() )
            rating = random.randint(1,5)\

            """ bad request like bad rating or bad type or missing sutff, missing prof """


            post_context = {
                "rating_value": rating,
                "rating_type": rating_type[0],
                "url": "/course/" + course.slug, # Should be removed after refactoring
                }
            if rating_type[0] == PROFESSOR_R:
                post_context['profname'] = random.choice(course.instructors.all()).name
            response = self.client.post('/rate_course', post_context)
            self.assertEqual(response.status_code, 404)

            post_context = {
                "course_id": course.id,
                "rating_type": rating_type[0],
                "url": "/course/" + course.slug,
                }
            if rating_type[0] == PROFESSOR_R:
                post_context['profname'] = random.choice(course.instructors.all()).name
            response = self.client.post('/rate_course', post_context)
            self.assertEqual(response.status_code, 404)

            post_context = {
                "course_id": course.id,
                "rating_value": rating,
                "rating_type": "NORATINGTYPETHATEXISTS",
                "url": "/course/" + course.slug,
                }
            if rating_type[0] == PROFESSOR_R:
                post_context['profname'] = random.choice(course.instructors.all()).name
            response = self.client.post('/rate_course', post_context)
            self.assertEqual(response.status_code, 404)

            post_context = {
                "course_id": course.id,
                "rating_value": 1000,
                "rating_type": rating_type[0],
                "url": "/course/" + course.slug,
                }
            if rating_type[0] == PROFESSOR_R:
                post_context['profname'] = random.choice(course.instructors.all()).name
            response = self.client.post('/rate_course', post_context)
            self.assertEqual(response.status_code, 404)

            if rating_type[0] == PROFESSOR_R:
                post_context = {
                    "course_id": course.id,
                    "rating_value": rating,
                    "rating_type": rating_type[0],
                    "url": "/course/" + course.slug,
                    }
                response = self.client.post('/rate_course', post_context)
                self.assertEqual(response.status_code, 404)

                post_context = {
                    "course_id": course.id,
                    "rating_value": rating,
                    "rating_type": rating_type[0],
                    "url": "/course/" + course.slug,
                    "profname": "NOT A PROFESSORS NAME"
                    }
                response = self.client.post('/rate_course', post_context)
                self.assertEqual(response.status_code, 404)

""" TODO: Also test for bad requests to login_required views """

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
