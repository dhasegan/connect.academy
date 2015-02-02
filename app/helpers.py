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

# Serialize the form errors to prepare them to be sent as message
def serialize_form_errors(request, form, prefix):
    field = {
        "email": "Your email",
        "username": "A username",
        "fname": "Your first name",
        "lname": "Your last name",
        "password": "A password",
        "password_confirmation": "Confirmation of the password"
    }
    field_errors = []
    for e in form.errors.keys():
        if e in field:
            field_errors.append(field[e] + " is required. Please enter it below!")
    errors = "<!>".join([e for e in field_errors + form.non_field_errors()])
    
    return prefix + errors