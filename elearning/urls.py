from django.urls import path
from . import views

urlpatterns = [
    path('', views.training_list, name='training_list'),
    path('training/<int:training_id>/', views.training_detail, name='training_detail'),
    path('module/<int:module_id>/', views.module_detail, name='module_detail'),
    path('module/<int:module_id>/complete/', views.complete_module, name='complete_module'),
    path('quiz/<int:quiz_id>/', views.take_quiz, name='take_quiz'),
    path('certificate/<int:certificate_id>/download/', views.download_certificate, name='download_certificate'),
    path('dashboard/', views.student_dashboard, name='student_dashboard'),
]
