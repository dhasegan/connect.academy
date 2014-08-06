import json

from django.core.context_processors import csrf
from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404, HttpResponse
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.views.decorators.http import require_GET, require_POST
from django.core.mail import send_mail
from django.db.models import Q

from app.models import *
from app.context_processors import *
from app.decorators import *
from app.manage.forms import *


@require_active_user
@login_required
def course_categories(request):
    context = {
        'page': 'course_categories',
    }
    category_tree = {
        'id': "root",
        'name': "My Categories",
        'data': {
            'type': 'category'  # category or course
        },
        'children': []
    }
    context.update(csrf(request))

    user = get_object_or_404(jUser, id=request.user.id)

    categories = user.categories_managed.all()
    for cat in categories:
        subtree = cat.get_subtree()
        category_tree['children'].append(subtree)
    context['category_tree'] = json.dumps(category_tree)

    potential_admins = jUser.objects.filter((Q(user_type=USER_TYPE_PROFESSOR) |
                                             Q(user_type=USER_TYPE_ADMIN))
                                            &
                                            Q(university=user.university)).order_by(
                                                'first_name')
    context['potential_admins'] = potential_admins

    categories = list(categories)
    all_categories = []
    all_categories += categories
    for cat in categories:
        all_categories += list(cat.get_descendants())
    context['all_categories'] = all_categories

    courses = []
    for cat in categories:
        courses += list(cat.get_all_courses())
    context['courses'] = courses

    return render(request, 'pages/admin.html', context)

# The admin forms.
#    Key: The value of the 'form_type' input of the form
#    Value: The class name of the form

forms = {
    # category forms
    'edit_category': EditCategoryForm,
    'new_subcat': NewSubcatForm,
    'remove_admin': RemoveAdminForm,
    'new_admin': NewAdminForm,
    'move_course': MoveCourseForm,
    'new_course': AddCourseForm,
    'delete_category': DeleteCategoryForm,
    # course forms
    'new_professor': NewProfessorForm,
    'remove_professor': RemoveProfessorForm,
    'move_to_category': MoveToCategoryForm,
    'edit_course': EditCourseForm,
    'delete_course': DeleteCourseForm,
    'move_category': MoveCategoryForm,
}


#
# Executes an admin form. Each admin form MUST have an input with key "form_type"  #
# The value of this input must be used as a key in the "forms" dictionary above    #
# linking to the correct Form object, which must be defined in admins/forms.py.    #
# Additionally, all Category forms must have an input with key "cat_id" and all    #
# Course forms must have an input with key "course_id" which specify the id of the #
# category/course being managed.                                                   #
# See also the documentation on forms.py                                           #
#
@require_POST
@require_active_user
@login_required
def admin_form_action(request):
    user = get_object_or_404(jUser, id=request.user.id)
    context = {
        'page': 'admin_form_action'
    }
    context.update(csrf(request))

    form_type = None
    if 'form_type' in request.POST:
        form_type = request.POST['form_type']
    else:
        raise Http404

    form = forms[form_type](request.POST)
    if form.is_valid() and form.is_allowed(user):
        response = form.execute_action()
        return HttpResponse(response, context)
    else:
        print dict(request.POST)
        print form.errors
        raise Http404
