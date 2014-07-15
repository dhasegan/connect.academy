from optparse import make_option

from django.core.management.base import BaseCommand

import versioning
from versioning.models import Revision
from versioning.utils import obj_diff


class Command(BaseCommand):

    args = "<appname.modelname ...>"

    help = "Setup django-versioning. Creates first revision for existent content."

    requires_model_validation = True

    option_list = BaseCommand.option_list + (
        make_option('-f', '--force', dest='force', action="store_true",
                    default=False, help='Kill existent revisions'),
    )

    def handle(self, *args, **options):
        from django.db.models import get_model

        models = [get_model(*i.split('.')) for i in args]
        if not models:
            models = versioning._registry.keys()

        for model in models:
            obj_empty = model()
            for obj in model.objects.order_by('pk').iterator():
                revisions = Revision.objects.get_for_object(obj)
                if len(revisions):
                    if not options.get('force'):
                        continue
                    else:
                        revisions.delete()
                Revision.objects.create(**{
                    'comment': 'Initial revision',
                    'delta': obj_diff(obj_empty, obj),
                    'content_object': obj,
                })
                self.stdout.write(
                    "{0}.{1}: {2}".format(
                        obj._meta.app_label,
                        obj._meta.object_name,
                        obj.pk
                    )
                )
