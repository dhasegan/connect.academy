from django.conf import settings

from app.models import *
from app.ratings import *


def explore_level_context(parents, checked=[]):
    context = []

    for parent in parents:
        categories = []
        none_checked = True
        for category in parent.children.all():
            if category.id in checked:
                none_checked = False
            categories.append({
                'category': category,
                'checked': category.id in checked
            })
        if len(categories) > 1:
            context.append({
                'categories': categories,
                'parent': parent,
                'name': parent.name,
                'none_checked': none_checked
            })
    return context


def explore_categories_context(checked=[]):
    context = []

    connect = Category.objects.get(parent=None)
    categories = [connect]
    while categories:
        context.append({
            'level': 0,
            'checkbox_groups': explore_level_context(categories, checked)
        })
        children_categories = []
        for category in categories:
            children = category.children.all()
            if len(children) > 1:
                for child in children:
                    if child.id in checked:
                        children_categories.append(child)
            elif len(children) == 1:
                children_categories.append(children[0])
        categories = children_categories
    return context


def course_timeline_context(courses, user):
    context = {}

    courses = sorted(courses, key=lambda x: x.name)

    credits = []
    allcourses = []
    for course in courses:
        if course.category is None:
            continue

        categories = []
        category = course.category
        course_path = None
        while category.parent is not None:
            categories.append(category)
            display_category = category.name if not category.abbreviation else category.abbreviation
            course_path = "%s > %s" % (display_category, course_path) if course_path else display_category
            category = category.parent
        categories = categories[::-1]  # reversed

        professors = [pcr.professor for pcr in course.professorcourseregistration_set.filter(is_approved=True)]

        # # This makes the explore page customizable for everyone
        # registration_status = course.get_registration_status(user)
        registration = course.get_registration_deadline()
        registration_open = registration.is_open() if registration is not None else False

        if course.credits not in credits:
            credits.append(course.credits)

        allcourses.append({
            'course': course,
            'professors': professors,
            # 'majors': course.majors.all(), # Majors not used yet
            'categories': categories,
            'course_path': course_path,
            'overall_rating': course.get_rating(OVERALL_R),
            # 'registration_status': registration_status,
            'registration_open': registration_open
        })
    context['courses'] = sorted(allcourses, key=lambda x: x['overall_rating'], reverse=True)

    context['credits'] = sorted(credits)
    return context
