import json

from django.conf import settings
from django.contrib.auth.models import AnonymousUser, User
from django.core.exceptions import PermissionDenied
from django.test import TestCase
from django.test.client import RequestFactory

from app.decider import decider

class DeciderTest(TestCase):

    """
    @title DeciderTest
    @description Tests the decider reader 
    """

    def setUp(self):
        settings.DECIDERS_VALUES = {
            "decider1": {
                "available": False,
                "users": []
            },
            "decider2": {
                "available": True,
                "users": []
            },
            "decider3": {
                "available": False,
                "users": ["decideruser"]
            },
            "decider4": {
                "available": True,
                "users": ["decideruser"]
            },
            "decider5": {
                "available": True
            },
        }
        user = User.objects.create_user(
            username='nouser', email='dh@ca', password='top_secret')
        self.request = RequestFactory().get('/any', {})
        self.request.user = user

    def testDeciderAvailability(self):
        self.assertEqual(decider.is_available("decider1"), False)
        self.assertEqual(decider.is_available("decider2"), True)
        self.assertEqual(decider.is_available("decider3"), False)
        self.assertEqual(decider.is_available("decider4"), True)
        self.assertEqual(decider.is_available("decider5"), True)
        self.assertEqual(decider.is_available("nodecider"), False)
        self.assertEqual(decider.is_available("decider1", "decideruser"), False)
        self.assertEqual(decider.is_available("decider2", "decideruser"), True)
        self.assertEqual(decider.is_available("decider3", "decideruser"), True)
        self.assertEqual(decider.is_available("decider4", "decideruser"), True)
        self.assertEqual(decider.is_available("decider1", "nouser"), False)
        self.assertEqual(decider.is_available("decider2", "nouser"), True)
        self.assertEqual(decider.is_available("decider3", "nouser"), False)
        self.assertEqual(decider.is_available("decider4", "nouser"), True)

    def testAvailableDeciders(self):
        u1_deciders = decider.available_deciders("decideruser")
        self.assertEqual(len(u1_deciders), 4)
        for k in ["decider2", "decider3", "decider4", "decider5"]:
            self.assertEqual(k in u1_deciders, True)

        u2_deciders = decider.available_deciders("nouser")
        self.assertEqual(len(u2_deciders), 3)
        for k in ["decider2", "decider4", "decider5"]:
            self.assertEqual(k in u2_deciders, True)

    def testDeciderForbidden(self):
        with self.assertRaises(PermissionDenied):
            decider.fail_on_unavailable(self.request, "decider1")
        decider.fail_on_unavailable(self.request, "decider2")
        with self.assertRaises(PermissionDenied):
            decider.fail_on_unavailable(self.request, "decider3")
