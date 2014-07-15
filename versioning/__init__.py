from __future__ import absolute_import, unicode_literals
_registry = {}


class AlreadyRegistered(Exception):
    pass


def register(model, fields=None):
    """
    """
    from django.conf import settings
    from django.db import models
    from django.db.models import signals as model_signals
    from versioning.signals import pre_save, post_save
    if 'modeltranslation' in settings.INSTALLED_APPS:
        from modeltranslation.translator import translator, NotRegistered
    else:
        translator = None

    opts = model._meta

    if fields is None:
        raise TypeError("You must give at least one field.")
    else:
        fields = list(fields)
        for field in fields[:]:
            f = opts.get_field(field)
            if isinstance(f, models.ManyToManyField):
                raise TypeError("""
                    versioning currently cannot handle ManyToManyField.
                    {0} is of type {1}
                    """.format(field, type(f))
                )
            if translator:
                try:
                    trans_opts = translator.get_options_for_model(model)
                    if field in trans_opts.fields:
                        fields[
                            fields.index(field) + 1:
                            fields.index(field) + 1
                        ] = [i.name for i in trans_opts.fields[field]]
                except NotRegistered:
                    pass

    if model in _registry:
        raise AlreadyRegistered
    _registry[model] = fields

    model_signals.pre_save.connect(pre_save, sender=model)
    model_signals.post_save.connect(post_save, sender=model)
