from django.conf.urls import patterns, include, url

urlpatterns = patterns('app.course.views',
    url(r'^$', 'course_page', name='course_page'),
    url(r'^image$', 'get_course_image', name='course_image'),
    url(r'^submit_review$', 'submit_review', name='submit_review'),
    url(r'^rate_course$', 'rate_course', name='rate_course'),
    url(r'^update_info$', 'update_info', name='update_info'),
    url(r'^update_syllabus$', 'update_syllabus', name='update_syllabus'),
    url(r'^delete_syllabus_entry$', 'delete_syllabus_entry', name='delete_syllabus_entry'),
    
    url(r'^submit_document$', 'submit_document', name='submit_document'),
    url(r'^resubmit_document$', 'resubmit_document', name='resubmit_document'),

    url(r'^submit_homework$', 'submit_homework', name='submit_homework'),
    url(r'^submit_homework_request$', 'submit_homework_request', name='submit_homework_request'),
    url(r'^submit_homework_grades$', 'submit_homework_grades', name='submit_homework_grades'),
    url(r'^edit_homework_request$', 'edit_homework_request', name='edit_homework_request'),
    url(r'^homework_dashboard$', 'homework_dashboard', name='homework_dashboard'),

    url(r'^create_group$', 'create_group', name='create_group'),
    url(r'^delete_group$', 'delete_group', name='delete_group'),

    url(r'^vote_review$', 'vote_review', name='vote_review'),
    url(r'^register$', 'register_course', name= 'register_course'),
    url(r'^send_mass_email$','send_mass_email',name='send_mass_email'),
    url(r'^load_course_activities$', 'load_course_activities', name='load_course_activities'),
    url(r'^load_new_course_activities$', 'load_new_course_activities', name='load_new_course_activities'),
)
