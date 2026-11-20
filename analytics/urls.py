from django.urls import path
from . import views

urlpatterns = [
    path('', views.professor_dashboard, name='professor_dashboard'),

    # Publications
    path('publications/', views.manage_publications, name='manage_publications'),
    path('publications/news/create/', views.create_news, name='create_news'),
    path('publications/news/<int:news_id>/edit/', views.edit_news, name='edit_news'),
    path('publications/news/<int:news_id>/delete/', views.delete_news, name='delete_news'),
    path('publications/news/<int:news_id>/toggle-publish/', views.toggle_news_publish, name='toggle_news_publish'),
    path('publications/news/<int:news_id>/toggle-pin/', views.toggle_news_pin, name='toggle_news_pin'),
    path('publications/news/<int:news_id>/preview/', views.preview_news, name='preview_news'),
    path('publications/research/create/', views.create_publication, name='create_publication'),
    path('publications/research/<int:pub_id>/edit/', views.edit_publication, name='edit_publication'),
    path('publications/research/<int:pub_id>/delete/', views.delete_publication, name='delete_publication'),

    # Courses
    path('courses/', views.manage_courses, name='manage_courses'),
    path('courses/create/', views.create_course, name='create_course'),
    path('courses/<int:course_id>/edit/', views.edit_course, name='edit_course'),
    path('courses/<int:course_id>/delete/', views.delete_course, name='delete_course'),
    path('courses/<int:course_id>/duplicate/', views.duplicate_course, name='duplicate_course'),
    path('courses/<int:course_id>/archive/', views.archive_course, name='archive_course'),

    # Course Resources
    path('resources/', views.manage_resources, name='manage_resources'),
    path('resources/course/<int:subject_id>/create/', views.create_resource, name='create_resource'),
    path('resources/<int:resource_id>/edit/', views.edit_resource, name='edit_resource'),
    path('resources/<int:resource_id>/delete/', views.delete_resource, name='delete_resource'),

    # E-learning
    path('elearning/', views.manage_elearning, name='manage_elearning'),
    path('elearning/training/create/', views.create_training, name='create_training'),
    path('elearning/training/<int:training_id>/edit/', views.edit_training, name='edit_training'),
    path('elearning/training/<int:training_id>/delete/', views.delete_training, name='delete_training'),
    path('elearning/training/<int:training_id>/module/create/', views.create_module, name='create_module'),
    path('elearning/module/<int:module_id>/edit/', views.edit_module, name='edit_module'),
    path('elearning/module/<int:module_id>/delete/', views.delete_module, name='delete_module'),
    path('elearning/modules/reorder/', views.reorder_modules, name='reorder_modules'),

    # Quiz
    path('elearning/module/<int:module_id>/quiz/create/', views.create_quiz, name='create_quiz'),
    path('elearning/quiz/<int:quiz_id>/edit/', views.edit_quiz, name='edit_quiz'),
    path('elearning/quiz/<int:quiz_id>/delete/', views.delete_quiz, name='delete_quiz'),
    path('elearning/quiz/<int:quiz_id>/questions/', views.manage_quiz_questions, name='manage_quiz_questions'),
    path('elearning/quiz/<int:quiz_id>/question/create/', views.create_question, name='create_question'),
    path('elearning/question/<int:question_id>/edit/', views.edit_question, name='edit_question'),
    path('elearning/question/<int:question_id>/delete/', views.delete_question, name='delete_question'),

    # Students
    path('students/', views.manage_students, name='manage_students'),
    path('students/<int:student_id>/detail/', views.student_detail, name='student_detail'),
    path('student/<int:user_id>/toggle-status/', views.toggle_student_status, name='toggle_student_status'),
    path('student/<int:user_id>/reset-progress/', views.reset_student_progress, name='reset_student_progress'),

    # Appointments
    path('appointments/', views.manage_appointments, name='manage_appointments'),
    path('appointments/<int:slot_id>/accept/', views.accept_appointment, name='accept_appointment'),
    path('appointments/<int:slot_id>/reject/', views.reject_appointment, name='reject_appointment'),
    path('appointments/<int:slot_id>/reschedule/', views.reschedule_appointment, name='reschedule_appointment'),

    # Notifications
    path('notifications/', views.manage_notifications, name='manage_notifications'),
    path('notifications/<int:notification_id>/read/', views.mark_notification_read, name='mark_notification_read'),
    path('notifications/<int:notification_id>/delete/', views.delete_notification, name='delete_notification'),

    # Profile
    path('profile/', views.manage_profile, name='manage_profile'),

    # Contact Messages
    path('messages/', views.manage_contact_messages, name='manage_contact_messages'),
    path('messages/<int:msg_id>/delete/', views.delete_contact_message, name='delete_contact_message'),

    # Exports
    path('export/csv/<str:report_type>/', views.export_csv_report, name='export_csv_report'),
    path('export/pdf/', views.export_pdf_report, name='export_pdf_report'),
]
