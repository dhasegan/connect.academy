from __future__ import absolute_import, unicode_literals
from django import forms
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from .models import Revision


class ReadOnlyInput(forms.Widget):
    """Don't allows to edit Revision.delta"""
    def render(self, name, value, attrs=None):
        return mark_safe("<div>{0}</div>".format(value))


class RevisionReadonlyForm(forms.ModelForm):

    reapply = forms.BooleanField(
        label=_("Reapply this revision"),
        required=False,
        widget=forms.CheckboxInput(attrs={
            'onclick': "this.form.submit()"
        })
    )
    delta_repr = forms.CharField(
        label=_("Diff"),
        required=False,
        widget=ReadOnlyInput()
    )

    def __init__(self, *a, **kw):
        """Instance constructor"""
        r = super(RevisionReadonlyForm, self).__init__(*a, **kw)
        if self.instance:
            self.initial['delta_repr'] = mark_safe(
                self.instance.display_diff()
            )
        return r

    class Meta:
        model = Revision
        fields = ("reapply", "delta_repr", )

    def save(self, *a, **kw):
        """Don't saves, only reapply if need."""
        if self.cleaned_data['reapply']:
            info = getattr(self.instance, 'revision_info', {})
            self.instance.reapply(
                editor_ip=info.get('editor_ip'),
                editor=info.get('editor'),
            )

        def save_m2m():
            pass

        self.save_m2m = save_m2m
        return self.instance
