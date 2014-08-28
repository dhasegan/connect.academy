
from app.models import *
import json

f = open('bin/combiner/courseDetails')
coursesList = json.load(f)
f.close()

univ = University.objects.filter(name__contains="Jacobs")[0]
category = univ.get_university_category()

# categories_tree = {}

abbreviations = {
    'Electrical Engineering and Computer Science': 'EECS',
    'Life Sciences': 'Life',
    'Logistics': 'Logistics',
    'Mathematical Sciences': 'Math',
    'Natural and Environmental Sciences': 'NatEnv',
    'Economics and Management': 'Econ',
    'History': 'History',
    'Humanities': 'Humanities',
    'Law': 'Law',
    'Psychology': 'Psych',
    'Social Sciences': 'Social',
    'Statistics and Methods': 'Stats',
    'University Studies Courses': 'USC',
    'German': 'German',
    'French': 'French',
    'Chinese': 'Chinese',
    'Spanish': 'Spanish',
    'Foundation Year': 'FY',
    "Fall": "Fall",
    "Engineering and Science": "EngSci",
    "Colloquia": "Colloquia",
    "Humanities and Social Sciences": "Humanities",
    "Language Courses": "Lang",
    "Undergraduate Level Courses": "Undergrad",
    "Graduate Level Courses": "Grad",
    "Spring": "Spring",
    "School of Engineering and Science": "SES",
    "School of Humanities and Social Sciences": "SHSS",
}

# all_cats = []

for courseDetails in coursesList:
    catalogue = courseDetails['Catalogue']
    categories = catalogue.split(" > ")
    current_category = category
    for cat in categories:
        # if not cat in all_cats:
        #     all_cats.append(cat)
        children = current_category.children.filter(name=cat)
        if not len(children):
            new_cat = Category.objects.create(parent=current_category, name=cat, level=current_category.level + 1,\
                university=univ, abbreviation=abbreviations[cat])
            current_category = new_cat
        else:
            current_category = children[0]

# cats_file = open("categories.json", "w")
# cats_file.write( json.dumps(all_cats) )
# cats_file.close()
