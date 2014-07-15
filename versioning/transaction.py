from functools import wraps
from threading import local
from .models import Revision
from .utils import obj_diff, obj_is_changed


class Transaction(object):

    def __init__(self,):
        """Constructor of Transaction instance."""
        self.ctx = local()

    @property
    def scopes(self):
        """Get transaction scopes."""
        if not hasattr(self.ctx, 'transaction_scopes'):
            self.ctx.transaction_scopes = []
        return self.ctx.transaction_scopes

    def begin(self):
        """Begin transaction."""
        if self.locked(+1):
            return
        self.scopes.append(set())
        return self

    def commit(self):
        """Commit transaction"""
        if self.locked(-1):
            return
        scope = self.scopes.pop()
        for obj in scope:
            self.post_save(obj)

    def rollback(self):
        """Commit transaction"""
        if self.locked(-1):
            return
        self.scopes.pop()

    def lock(self):
        self.ctx.locked = 0
        return self

    def locked(self, val=None):
        if not hasattr(self.ctx, 'locked'):
            return False
        if val is not None:
            self.ctx.locked += val
        if self.ctx.locked == 0:
            delattr(self.ctx, 'locked')
            return False
        return True

    def add_obj(self, obj):
        """Adds object"""
        self.pre_save(obj)
        self.scopes[-1].add(obj)

    def pre_save(self, obj):
        """Pre-save object"""
        model = obj.__class__
        if not hasattr(obj, 'revision_info'):
            obj.revision_info = {}
        info = obj.revision_info

        try:
            prev = model._default_manager.get(pk=obj.pk)
        except model.DoesNotExist:
            prev = model()

        if not obj_is_changed(prev, obj):
            obj.revision_info = {}
            return

        info['delta'] = obj_diff(prev, obj)
        request = getattr(self.ctx, 'request', None)
        if request:
            if not info.get('editor'):
                info['editor'] = request.user
            if not info.get('editor_ip'):
                info['editor_ip'] = request.META.get("REMOTE_ADDR")
        if not getattr(info.get('editor'), 'pk', None):  # Anonymuous
            info['editor'] = None

    def post_save(self, obj):
        """Post-save object"""
        info = getattr(obj, 'revision_info', {})
        if info:
            rev = Revision(**info)
            rev.content_object = obj
            rev.save()

    def __call__(self, f=None):
        if f is None:
            return self

        @wraps(f)
        def _decorated(*args, **kw):
            with self:
                rv = f(*args, **kw)
            return rv

        return _decorated

    def __enter__(self):
        self.begin()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.rollback()
        else:
            try:
                self.commit()
            except:
                self.rollback()
                raise

transaction = Transaction()
