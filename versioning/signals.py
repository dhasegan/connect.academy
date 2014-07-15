from __future__ import absolute_import, unicode_literals
from .transaction import transaction


def pre_save(sender, instance, **kwargs):
    """Pre-save signal handler"""
    transaction.begin()
    transaction.add_obj(instance)


def post_save(sender, instance, **kwargs):
    """Post-save signal handler"""
    transaction.commit()
