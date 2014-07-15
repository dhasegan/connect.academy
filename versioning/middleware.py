from __future__ import absolute_import, unicode_literals
from django.conf import settings
from .transaction import transaction


def get_request():
    """Get request object from any location of code."""
    return getattr(transaction.ctx, 'request', None)


class VersioningMiddleware(object):
    """Middleware that saves request in thread local storage"""

    def process_request(self, request):
        transaction.ctx.request = request
        transaction.begin()
        if getattr(settings, 'VERSIONING_ATOMIC_REQUESTS', False):
            transaction.lock()

    def process_exception(self, request, exception):
        transaction.rollback()

    def process_response(self, request, response):
        if transaction.scopes:
            # if self.process_exception() hasn't called
            transaction.commit()
        return response
