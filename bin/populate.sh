#!/bin/sh

python manage.py shell --plain < bin/populate/populate_professors.py
python manage.py shell --plain < bin/populate/populate_categories.py
python manage.py shell --plain < bin/populate/populate_db.py
python manage.py shell --plain < bin/populate/populate_appointments.py
python manage.py shell --plain < bin/jcourse/populate.py
