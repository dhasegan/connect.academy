from __future__ import absolute_import, unicode_literals
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from django.views.generic import ListView, UpdateView

from .forms import RevisionReadonlyForm
from .models import Revision


class RevisionReapplyView(UpdateView):
    """Reapples Revision"""
    form_class = RevisionReadonlyForm
    queryset = Revision.objects.all()

    def get_object(self, queryset=None):
        """Returns object for current request. Also checks permissions."""
        obj = super(RevisionReapplyView, self).get_object(queryset)
        content_object = obj.content_object
        perm = '{app}.{perm}_{mod}'.format(
            app=content_object._meta.app_label,
            perm='reapply_revision',
            mod=content_object._meta.module_name
        )
        #if not self.request.user.has_perm(perm, obj.content_object):
            #raise PermissionDenied
        return obj

    def form_valid(self, form):
        """Binds to object the editor's info"""
        form.instance.revision_info = {
            'editor_ip': self.request.META.get("REMOTE_ADDR"),
            'editor': self.request.user
        }
        return super(RevisionReapplyView, self).form_valid(form)

    def get_success_url(self):
        """Returns content_object url"""
        return self.object.content_object.get_absolute_url()

    # @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(RevisionReapplyView, self).dispatch(request, *args, **kwargs)


class RevisionListView(ListView):
    """List of revisions"""
    queryset = Revision.objects.all()

    def get_queryset(self):
        """Returns queryset for current request. Also, check permissions."""
        content_type = self.kwargs.get('content_type', None)
        object_id = self.kwargs.get('object_id', None)
        content_type = get_object_or_404(ContentType, pk=content_type)
        try:
            content_object = content_type.get_object_for_this_type(pk=object_id)
            self.content_object = content_object
        except content_type.model_class().DoesNotExist:
            raise Http404
        qs = self.queryset.filter(
            content_type=content_type,
            object_id=content_object.pk
        )
        perm = '{app}.{perm}_{mod}'.format(
            app=content_object._meta.app_label,
            perm='browse_revision',
            mod=content_object._meta.module_name
        )
        #if not self.request.user.has_perm(perm, content_object):
         #   raise PermissionDenied
        return qs

    def get_context_data(self, **kwargs):
        """Get the context for this view."""
        context = super(RevisionListView, self).get_context_data(**kwargs)
        context.update({
            'content_object': self.content_object,
        })
        return context

    # @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(RevisionListView, self).dispatch(request, *args, **kwargs)
