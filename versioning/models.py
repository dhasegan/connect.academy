from __future__ import absolute_import, unicode_literals
import copy
import hashlib
try:
    from django.utils import timezone as datetime
except ImportError:
    from datetime import datetime

from django.db import models, IntegrityError
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.utils.encoding import force_unicode
from django.utils.translation import ugettext_lazy as _
from django.conf import settings

from .managers import RevisionManager
from .utils import apply_diff, display_diff

try:
    str = unicode  # Python 2.* compatible
except NameError:
    pass

UserModel = getattr(settings, 'AUTH_USER_MODEL', 'auth.User')


class Revision(models.Model):
    """
    A single revision for an object.
    """
    object_id = models.CharField(max_length=255, db_index=True)
    content_type = models.ForeignKey(ContentType)
    content_object = generic.GenericForeignKey("content_type", "object_id")

    revision = models.IntegerField(_("Revision Number"), db_index=True)
    reverted = models.BooleanField(_("Reverted Revision"), default=False,
                                   db_index=True)
    sha1 = models.CharField(max_length=40, db_index=True)
    delta = models.TextField()

    created_at = models.DateTimeField(_("Created at"), default=datetime.now,
                                      db_index=True)
    comment = models.CharField(_("Editor comment"), max_length=255,
                               blank=True)

    editor = models.ForeignKey(UserModel, verbose_name=_('Editor'),
                               blank=True, null=True,
                               on_delete=models.SET_NULL)
    editor_ip = models.IPAddressField(_("IP Address of the Editor"),
                                      blank=True, null=True)

    objects = RevisionManager()

    class Meta:
        verbose_name = _('Revision')
        verbose_name_plural = _('Revisions')
        get_latest_by = 'id'
        ordering = ('-id',)
        unique_together = (("object_id", "content_type", "revision"),)

    def __str__(self):
        return "r{0} {1} {2}".format(self.revision, self.sha1,
                                     self.content_object)

    def save(self, *a, **kw):
        """ Saves the article with a new revision.
        """
        self.sha1 = hashlib.sha1(
            force_unicode(self.delta).encode("utf-8")
        ).hexdigest()
        if self.id is None:
            try:
                self.revision = Revision.objects.get_for_object(
                    self.content_object
                ).latest().revision + 1
            except self.DoesNotExist:
                self.revision = 1
        attempt = 0
        while True:
            try:
                super(Revision, self).save(*a, **kw)
                break
            except IntegrityError:
                self.revision += 1
                attempt += 1
                if attempt > 20:
                    raise

    def is_anonymous_change(self):
        """Returns True if editor is not authenticated."""
        return self.editor is None

    def get_content_object_version(self, prev=False):
        """Returns content_object for this revision"""
        obj = copy.copy(self.content_object)

        next_changes = Revision.objects.get_for_object(
            obj
        ).filter(**{
            'revision__gte' if prev else 'revision__gt': self.revision
        }).order_by('-revision')

        for changeset in next_changes:
            apply_diff(obj, changeset.delta)

        return obj

    @property
    def content_object_version(self):
        return self.get_content_object_version()

    def reapply(self, editor_ip=None, editor=None):
        """
        Returns the Content object to this revision.
        """
        obj = self.content_object_version
        obj.revision_info = {
            'comment': "Reverted to revision #{0}".format(self.revision),
            'editor_ip': editor_ip,
            'editor': editor
        }

        Revision.objects.get_for_object(
            obj
        ).filter(
            revision__gt=self.revision
        ).update(reverted=True)

        obj.save()

    def display_diff(self):
        """Returns a HTML representation of the diff."""

        if not self.delta:
            return ""

        obj_current = self.content_object_version
        obj_prev = self.get_content_object_version(prev=True)

        return display_diff(obj_prev, obj_current)

# Python 2.* compatible
try:
    unicode
except NameError:
    pass
else:
    for cls in (Revision, ):
        cls.__unicode__ = cls.__str__
        cls.__str__ = lambda self: self.__unicode__().encode('utf-8')
