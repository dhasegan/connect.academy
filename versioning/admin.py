from __future__ import absolute_import, unicode_literals
from django.conf import settings
from django.contrib import admin

from . import _registry
from .forms import RevisionReadonlyForm
from .models import Revision
from .utils import diff_split_by_fields


class RevisionAdmin(admin.ModelAdmin):
    form = RevisionReadonlyForm
    list_display = ("pk", "revision", "sha1", "content_type",
                    "object_id", 'content_object', "created_at",
                    "editor", "comment", "editor_ip", "reverted",)
    list_filter = ("created_at", "content_type", )
    search_fields = ("delta", "comment", )
    fields = ("reapply", "delta_repr", )
    ordering = ('-id', )

    def save_form(self, request, form, change, *a, **kw):
        """Binds to object the editor's info"""
        form.instance.revision_info = {
            'editor_ip': request.META.get("REMOTE_ADDR"),
            'editor': request.user
        }
        return super(RevisionAdmin, self).save_form(
            request, form, change, *a, **kw
        )

    def has_delete_permission(self, request, obj=None):
        """Allows to delete only first or diff-empty revisions"""
        parent = super(RevisionAdmin, self)\
            .has_delete_permission(request, obj)
        if not parent or not obj:
            return False

        # Is it first revision?
        previouses = Revision.objects.get_for_object(obj.content_object)\
            .filter(revision__lt=obj.revision)
        if not previouses.count():
            return True

        # Is revision has an empty diff?
        diffs = diff_split_by_fields(obj.delta)
        if not "".join(list(diffs.values())).strip():
            return True

        return False

admin.site.register(Revision, RevisionAdmin)


class AdminVersionableMixIn(object):
    """Versionable Admin class"""
    object_history_template = 'versioning/admin/object_history.html'

    def save_model(self, request, obj, form, change, *a, **kw):
        """Binds to object the editor's info"""
        obj.revision_info = {
            'editor_ip': request.META.get("REMOTE_ADDR"),
            'editor': request.user
        }
        return super(AdminVersionableMixIn, self).save_model(
            request, obj, form, change, *a, **kw
        )


def make_admin_versionable(cls):
    """Make Admin class versionable"""
    class AdminVersionable(AdminVersionableMixIn, cls):
        pass

    return AdminVersionable


def autodiscover():
    """Adds RevisionInline for revisionable models."""
    for model in _registry:
        if model in admin.site._registry:
            model_admin = admin.site._registry[model]
            if not isinstance(model_admin, AdminVersionableMixIn):
                cls = model_admin.__class__
                admin.site.unregister(model)
                admin.site.register(model, make_admin_versionable(cls))

if getattr(settings, 'VERSIONING_ADMIN_AUTODISCOVER', True):
    autodiscover()
