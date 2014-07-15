from __future__ import absolute_import, unicode_literals
from django.db import models
from django.contrib.contenttypes.models import ContentType


class RevisionManager(models.Manager):
    """Revision manager"""

    def get_for_object(self, obj):
        """Query set for given object"""
        ct = ContentType.objects.get_for_model(obj)
        return self.filter(content_type__pk=ct.pk, object_id=obj.pk)

    def get_non_reverted_for_object(self, obj):
        """Query set of non reverted revisions for given object"""
        return self.get_for_object(obj).filter(reverted=False)
