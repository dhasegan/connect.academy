# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from datetime import date, timedelta
from django.db import models
from django.conf import settings
from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.core import urlresolvers
from django.http import HttpResponse
from django.test import TestCase
from django.utils.importlib import import_module
from django.utils.timezone import now

import versioning
from .admin import autodiscover
from .models import Revision


class TestFkModel(models.Model):
    attr_text = models.TextField(blank=True)

    class Meta:
        db_table = 'versioning_testfkmodel'


class TestModel(models.Model):
    attr_text = models.TextField(blank=True)
    attr_bool = models.NullBooleanField(blank=True)
    attr_int = models.IntegerField(blank=True, null=True)
    attr_fk = models.ForeignKey(TestFkModel, blank=True, null=True)
    attr_fk_notnull = models.ForeignKey(TestFkModel, related_name='foreign_key_notnull')
    attr_datetime = models.DateTimeField(default=now)
    attr_date = models.DateField(default=date.today)
    attr_datetimenull = models.DateTimeField(blank=True, null=True)
    attr_datenull = models.DateField(blank=True, null=True)

    class Meta:
        db_table = 'versioning_testmodel'

    def get_absolute_url(self):
        return urlresolvers.reverse('versioning_testmodel', args=(self.pk,))

versioning.register(
    TestModel,
    ['attr_text', 'attr_int', 'attr_bool', 'attr_fk', 'attr_fk_notnull',
     'attr_datetime', 'attr_date', 'attr_datetimenull', 'attr_datenull']
)


class TestModelAdmin(admin.ModelAdmin):
    pass

admin.site.register(TestModel, TestModelAdmin)
# admin.autodiscover()
autodiscover()

urlconf_module = import_module(settings.ROOT_URLCONF)
urlpatterns = patterns(
    '',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^testmodel/(?P<pk>\d+)/', lambda request, pk: HttpResponse("Ok"), name='versioning_testmodel')
) + urlconf_module.urlpatterns


class VersioningForAdminTest(TestCase):

    urls = 'versioning.tests'

    def setUp(self):
        self.admin = User.objects.create_superuser(
            username='admin',
            email="admin@mailinator.com",
            password="adminpwd"
        )
        response = self.client.login(username='admin', password='adminpwd')
        self.assertTrue(response)

    def test_diffs(self):
        obj_fk_1 = TestFkModel.objects.create(
            attr_text="техт",
        )
        obj_fk_2 = TestFkModel.objects.create(
            attr_text="техт",
        )
        obj_1 = TestModel(
            attr_text="строка первая\nстрока вторая\nстрока третья",
            attr_fk=None,
            attr_fk_notnull=obj_fk_1,
            attr_int=1
        )
        obj_1.revision_info = {
            'editor': self.admin,
            'comment': 'comment 1',
        }
        obj_1.save()
        self.assertEqual(Revision.objects.get_for_object(obj_1).count(), 1)

        obj_1.attr_text = obj_1.attr_text
        obj_1.save()  # Not changed
        self.assertEqual(Revision.objects.get_for_object(obj_1).count(), 1)

        obj_2 = TestModel.objects.get(pk=obj_1.pk)
        obj_2.attr_text = "строка первая\nстрока измененная вторая\nстрока третья"
        obj_2.attr_bool = True
        obj_2.attr_fk = obj_fk_1
        obj_2.attr_fk_notnull = obj_fk_1
        obj_2.attr_datetime += timedelta(days=2)
        obj_2.attr_date += timedelta(days=2)
        obj_2.attr_datetimenull = now()
        obj_2.attr_datenull = date.today()
        obj_2.revision_info = {
            'editor': self.admin,
            'comment': 'comment 1',
        }
        obj_2.save()
        self.assertEqual(Revision.objects.get_for_object(obj_1).count(), 2)

        obj_3 = TestModel.objects.get(pk=obj_1.pk)
        obj_3.attr_text = "строка первая\nстрока измененная снова вторая\nстрока третья"
        obj_3.attr_bool = False
        obj_3.attr_int = 3
        obj_3.attr_fk = obj_fk_2
        obj_3.attr_fk_notnull = obj_fk_2
        obj_3.attr_datetime += timedelta(days=2)
        obj_3.attr_date += timedelta(days=2)
        obj_3.attr_datetimenull = None
        obj_3.attr_datenull = None
        obj_3.revision_info = {
            'editor': self.admin,
            'comment': 'comment 1',
        }
        obj_3.save()
        self.assertEqual(Revision.objects.get_for_object(obj_1).count(), 3)

        rev_1 = Revision.objects.get_for_object(obj_1).order_by('pk')[0]
        self.assertEqual(rev_1.revision, 1)

        rev_1.display_diff()
        rev_1.reapply()

        obj_4 = TestModel.objects.get(pk=obj_1.pk)
        self.assertEqual(obj_4.attr_text, obj_1.attr_text)
        self.assertEqual(obj_4.attr_bool, obj_1.attr_bool)
        self.assertEqual(obj_4.attr_fk, obj_1.attr_fk)
        self.assertEqual(obj_4.attr_fk_notnull, obj_1.attr_fk_notnull)
        self.assertEqual(obj_4.attr_datetime, obj_1.attr_datetime)
        self.assertEqual(obj_4.attr_date, obj_1.attr_date)
        self.assertEqual(Revision.objects.get_for_object(obj_1).count(), 4)

        rev_2 = Revision.objects.get_for_object(obj_1).order_by('pk')[1]
        self.assertEqual(rev_2.revision, 2)

        rev_2.display_diff()
        rev_2.reapply()

        obj_5 = TestModel.objects.get(pk=obj_2.pk)
        self.assertEqual(obj_5.attr_text, obj_2.attr_text)
        self.assertEqual(obj_5.attr_bool, obj_2.attr_bool)
        self.assertEqual(obj_5.attr_fk, obj_2.attr_fk)
        self.assertEqual(obj_5.attr_fk_notnull, obj_2.attr_fk_notnull)
        self.assertEqual(obj_5.attr_datetime, obj_2.attr_datetime)
        self.assertEqual(obj_5.attr_date, obj_2.attr_date)
        self.assertEqual(Revision.objects.get_for_object(obj_2).count(), 5)

    def test_views(self):
        obj_fk_1 = TestFkModel.objects.create(
            attr_text="техт",
        )
        obj_1 = TestModel(
            attr_text="строка первая\nстрока вторая\nстрока третья",
            attr_fk=None,
            attr_fk_notnull=obj_fk_1,
            attr_int=1
        )
        obj_1.revision_info = {
            'editor': self.admin,
            'comment': 'comment 1',
        }
        obj_1.save()
        self.assertEqual(Revision.objects.get_for_object(obj_1).count(), 1)

        obj_2 = TestModel.objects.get(pk=obj_1.pk)
        obj_2.attr_text = "строка первая\nстрока измененная вторая\nстрока третья"
        obj_2.attr_bool = True
        obj_2.attr_fk = obj_fk_1
        obj_2.attr_fk_notnull = obj_fk_1
        obj_2.revision_info = {
            'editor': self.admin,
            'comment': 'comment 1',
        }
        obj_2.save()
        self.assertEqual(Revision.objects.get_for_object(obj_1).count(), 2)

        obj_3 = TestModel.objects.get(pk=obj_1.pk)
        obj_3.attr_text = "строка первая\nстрока измененная снова вторая\nстрока третья"
        obj_3.attr_bool = False
        obj_3.attr_int = 3
        obj_3.revision_info = {
            'editor': self.admin,
            'comment': 'comment 1',
        }
        obj_3.save()
        self.assertEqual(Revision.objects.get_for_object(obj_1).count(), 3)

        response = self.client.get(urlresolvers.reverse('versioning_revision_list', kwargs={
            'content_type': ContentType.objects.get_for_model(TestModel).pk,
            'object_id': obj_1.pk
        }))
        self.assertEqual(response.status_code, 200)
        revisions = Revision.objects.get_for_object(obj_1)
        self.assertEqual(len(revisions), 3)

        for r in revisions:
            self.assertContains(response, urlresolvers.reverse('versioning_revision_reapply', args=(r.pk,)))

        r = revisions[1]
        response = self.client.get(urlresolvers.reverse('versioning_revision_reapply', args=(r.pk,)))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'name="reapply"')
        self.assertContains(response, 'onclick="this.form.submit()"')

        response = self.client.post(
            urlresolvers.reverse('versioning_revision_reapply', args=(r.pk,)),
            {'reapply': 1}
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, obj_1.get_absolute_url(), 302)
        self.assertEqual(Revision.objects.get_for_object(obj_1).count(), 4)
        self.assertEqual(
            TestModel.objects.get(pk=obj_1.pk).attr_text,
            "строка первая\nстрока измененная вторая\nстрока третья"
        )

    def test_admin(self):
        obj_fk_1 = TestFkModel.objects.create(
            attr_text="техт",
        )
        obj_1 = TestModel(
            attr_text="строка первая\nстрока вторая\nстрока третья",
            attr_fk=None,
            attr_fk_notnull=obj_fk_1,
            attr_int=1
        )
        obj_1.revision_info = {
            'editor': self.admin,
            'comment': 'comment 1',
        }
        obj_1.save()
        self.assertEqual(Revision.objects.get_for_object(obj_1).count(), 1)

        obj_2 = TestModel.objects.get(pk=obj_1.pk)
        obj_2.attr_text = "строка первая\nстрока измененная вторая\nстрока третья"
        obj_2.attr_bool = True
        obj_2.attr_fk = obj_fk_1
        obj_2.attr_fk_notnull = obj_fk_1
        obj_2.revision_info = {
            'editor': self.admin,
            'comment': 'comment 1',
        }
        obj_2.save()
        self.assertEqual(Revision.objects.get_for_object(obj_1).count(), 2)

        obj_3 = TestModel.objects.get(pk=obj_1.pk)
        obj_3.attr_text = "строка первая\nстрока измененная снова вторая\nстрока третья"
        obj_3.attr_bool = False
        obj_3.attr_int = 3
        obj_3.revision_info = {
            'editor': self.admin,
            'comment': 'comment 1',
        }
        obj_3.save()
        self.assertEqual(Revision.objects.get_for_object(obj_1).count(), 3)

        response = self.client.get(urlresolvers.reverse('admin:versioning_testmodel_history', args=(obj_1.pk,)))
        self.assertEqual(response.status_code, 200)
        revisions = Revision.objects.get_for_object(obj_1)
        self.assertEqual(len(revisions), 3)

        for r in revisions:
            self.assertContains(response, urlresolvers.reverse('admin:versioning_revision_change', args=(r.pk,)))

        r = revisions[1]
        response = self.client.get(urlresolvers.reverse('admin:versioning_revision_change', args=(r.pk,)))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'name="reapply"')
        self.assertContains(response, 'onclick="this.form.submit()"')

        response = self.client.post(
            urlresolvers.reverse('admin:versioning_revision_change', args=(r.pk,)),
            {'reapply': 1}
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, urlresolvers.reverse('admin:versioning_revision_changelist'), 302)
        self.assertEqual(Revision.objects.get_for_object(obj_1).count(), 4)
        self.assertEqual(
            TestModel.objects.get(pk=obj_1.pk).attr_text,
            "строка первая\nстрока измененная вторая\nстрока третья"
        )
