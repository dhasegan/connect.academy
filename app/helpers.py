from django.utils.text import slugify

def get_slug_for(Model, pk, name):
    original_slug = slugify(name)
    objects = Model.objects.filter(slug__startswith=original_slug).exclude(pk=pk)
    same_slug_objects = [obj.slug for obj in objects]
    slug = original_slug
    if slug in same_slug_objects:
        for appendix in range(1, len(same_slug_objects)+1):
            slug = original_slug + "-" + str(appendix)
            if not slug in same_slug_objects:
                break
    return slug